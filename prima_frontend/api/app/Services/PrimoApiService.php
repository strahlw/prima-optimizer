<?php

namespace App\Services;

use App\Enum\TaskStatus;
use App\Exceptions\PrimoApiException;
use App\Exceptions\PrimoValidationException;
use App\Http\TaskStatusResponse;
use App\Models\Project;
use App\Models\Scenario;
use App\Repositories\DataImportRepository;
use App\Types\GeneralSpecifications;
use App\Types\RankOnlyScenarioData;
use App\Types\RecommendationOnlyScenarioData;
use App\Types\ScenarioData;
use Carbon\Carbon;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Arr;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class PrimoApiService
{
    protected string $baseUri;

    public function __construct()
    {
        $this->baseUri = config('app.python_api_url');
    }

    /**
     * Verifies the response status type.
     *
     * @param  Response  $response  The response object.
     *
     * @throws PrimoApiException If the status type is invalid.
     */
    protected function verifyResponseStatusType(Response $response): void
    {
        $status = $response->json('status');
        if (TaskStatus::hasValue($status) === false) {
            throw new PrimoApiException("Invalid status type: $status, ".json_encode($response->json()));
        }
    }

    /**
     * Parse the date or return the current date.
     */
    protected function parseDate(?string $date): Carbon
    {
        return $date ? Carbon::parse($date) : now();
    }

    /**
     * Send a GET request.
     */
    protected function sendGetRequest(string $endpoint): Response
    {
        return Http::timeout(5)->get($this->baseUri.$endpoint);
    }

    /**
     * Handle response errors.
     */
    protected function handleErrorResponse(Response $response, string $message): void
    {
        // TODO: Modify this to not just return the body, but more specific messages
        if ($response->unprocessableEntity()) {
            throw new PrimoApiException("$message: ".$response->body(), 422);
        }

        throw new PrimoApiException("$message: ".$response->body());
    }

    /**
     * Verifies the connection to the Primo API.
     */
    public function verifyConnection(): bool
    {
        try {
            $response = $this->sendGetRequest('/ping');
            if (! $response->ok()) {
                $this->handleErrorResponse($response, 'Primo API connection failed');
            }

            return true;
        } catch (\Exception $e) {
            throw new PrimoApiException("Python API connection failed: {$e->getMessage()}");
        }
    }

    /**
     * Get the uptime from the Primo API.
     */
    public function getUptime(): Response
    {
        try {
            $response = $this->sendGetRequest('/uptime');
            if (! $response->ok()) {
                $this->handleErrorResponse($response, 'Primo API uptime request failed');
            }

            return $response;
        } catch (\Exception $e) {
            throw new PrimoApiException("Python API uptime request failed: {$e->getMessage()}");
        }
    }

    /**
     * Verifies the Primo API connection to Redis.
     */
    public function verifyRedisConnection(): bool
    {
        try {
            $response = Http::get($this->baseUri.'/redis_check');
            if (! $response->ok()) {
                $this->handleErrorResponse($response, 'Redis connection failed');
            }

            return true;
        } catch (\Exception $e) {
            throw new PrimoApiException("Redis connection failed: {$e->getMessage()}");
        }
    }

    /**
     * Verifies the Primo API connection to Mongo.
     */
    public function verifyMongoConnection(): bool
    {
        try {
            $response = Http::get($this->baseUri.'/mongo_check');
            if (! $response->ok()) {
                $this->handleErrorResponse($response, 'MongoDB connection failed');
            }

            return true;
        } catch (\Exception $e) {
            throw new PrimoApiException("MongoDB connection failed: {$e->getMessage()}");
        }
    }

    /**
     * Retrieves the status of a task.
     *
     * @param  string  $taskId  The ID of the task.
     * @return TaskStatusResponse The response containing the status of the task.
     */
    public function getTaskStatus(string $taskId): TaskStatusResponse
    {
        try {
            $response = $this->sendGetRequest("/status/$taskId");

            if ($response->ok()) {
                $this->verifyResponseStatusType($response);
                $data = (object) $response->json();
                $date = $this->parseDate($data->date ?? null);

                return new TaskStatusResponse($data->id, $data->status, $date, $data->description ?? '');
            }

            $this->handleErrorResponse($response, "Task status request failed for task ID: $taskId");
        } catch (\Exception $e) {
            Log::error($e->getTraceAsString());
            throw new PrimoApiException("Failed to get task status: {$e->getMessage()}");
        }
    }

    /**
     * Runs optimization using the provided data.
     *
     * @param  ScenarioData  $data  The data for optimization.
     * @return TaskStatusResponse The response containing the status of the optimization task.
     */
    public function runOptimization(ScenarioData|RecommendationOnlyScenarioData $data, int $scenarioId): TaskStatusResponse
    {
        try {
            $data->scenario_id = $scenarioId;
            $response = Http::post($this->baseUri.'/run_primo', $data);

            if ($response->ok()) {
                $this->verifyResponseStatusType($response);
                $data = (object) $response->json();
                $date = $this->parseDate($data->date ?? null);

                return new TaskStatusResponse($data->id, $data->status, $date);
            } else {
                throw $this->createScenarioErrorResponse($response);
            }
        } catch (\Exception $e) {
            throw new PrimoApiException("Optimization run failed: {$e->getMessage()}");
        }
    }

    public function createOverrideScenario(Scenario $parentScenario, Scenario $childScenario, array $overrideData)
    {
        try {
            $scenarioData = $parentScenario->data;
            $scenarioData['use_cases'] = $parentScenario->useCases;
            $scenarioData['scenario_id'] = $parentScenario->id;

            $allData = [
                $overrideData,
                (array) $scenarioData,
            ];
            $wellsRemoveTotal = [];

            foreach ($overrideData['projects_remove'] as $projectId) {
                $project = Project::where('id', $projectId)->where('scenario_id', $parentScenario->id)->first();
                $wellsRemoveTotal[$projectId] = $project->getWells()->pluck('json.well_id')->values();
            }

            if (! empty($overrideData['wells_remove'])) {
                $wellsRemoveTotal = $wellsRemoveTotal + $overrideData['wells_remove'];
            }

            // Convert wells_remove object ids to well_ids
            // TODO: revisit + cleanup implementation
            if (! empty($overrideData['wells_remove'])) {
                $transformedWellsRemove = [];
                foreach ($overrideData['wells_remove'] as $projectId => $wellObjectIds) {
                    $project = Project::find($projectId);
                    if ($project) {
                        $wells = $project->getWells()->filter(function ($well) use ($wellObjectIds) {
                            return in_array($well->id, $wellObjectIds);
                        });

                        $wellIds = $wells->pluck('well_id')->toArray();

                        $transformedWellsRemove[$projectId] = $wellIds;
                    }
                }
                $wellsRemoveTotal = $transformedWellsRemove;
            }

            $requestData = Arr::collapse($allData);
            $requestData['child_scenario_id'] = $childScenario->id;
            $requestData['name'] = $childScenario->data['name'];
            $requestData['projects_remove'] = empty($overrideData['projects_remove']) ? [] : $overrideData['projects_remove'];
            $requestData['wells_remove'] = empty($wellsRemoveTotal) ? new \stdClass : (object) $wellsRemoveTotal;
            $requestData['projects_lock'] = empty($overrideData['projects_lock']) ? [] : $overrideData['projects_lock'];
            $requestData['wells_lock'] = empty($overrideData['wells_lock']) ? new \stdClass : $overrideData['wells_lock'];
            $requestData['wells_reassign_from'] = empty($overrideData['wells_reassign_from']) ? new \stdClass : $overrideData['wells_reassign_from'];
            $requestData['wells_reassign_to'] = empty($overrideData['wells_reassign_to']) ? new \stdClass : (object) $overrideData['wells_reassign_to'];
            $requestData['parent_project_ids'] = $parentScenario->projects->pluck('id')->toArray();

            $response = Http::post($this->baseUri.'/manual_override_recalculation', $requestData);
            if ($response->ok()) {
                $this->verifyResponseStatusType($response);
                $data = (object) $response->json();
                $date = $this->parseDate($data->date ?? null);

                return new TaskStatusResponse($data->id, $data->status, $date);
            } else {
                throw $this->createScenarioErrorResponse($response);
            }
        } catch (\Exception $e) {
            throw new PrimoApiException("Override scenario creation failed: {$e->getMessage()}");
        }
    }

    public function runRanking(ScenarioData|RankOnlyScenarioData|RecommendationOnlyScenarioData $data)
    {
        try {
            $response = Http::post($this->baseUri.'/rank_wells', $data);
            if ($response->ok()) {
                $data = (object) $response->json();
                $date = $this->parseDate($data->date ?? null);

                return new TaskStatusResponse($data->id, $data->status, $date);
            } else {
                throw $this->createScenarioErrorResponse($response);
            }
        } catch (\Exception $e) {
            throw new PrimoApiException("Ranking failed: {$e->getMessage()}");
        }
    }

    /**
     * Kills the optimization task with the specified task ID.
     *
     * @param  string  $taskId  The ID of the optimization task to kill.
     * @return TaskStatusResponse The response containing the status of the task after killing it.
     */
    public function killOptimization(string $taskId): TaskStatusResponse
    {
        try {
            $response = Http::delete($this->baseUri."/kill/$taskId");

            if ($response->ok()) {
                $this->verifyResponseStatusType($response);
                $data = (object) $response->json();
                $date = $this->parseDate($data->date ?? null);

                return new TaskStatusResponse($data->id, $data->status, $date);
            }

            $this->handleErrorResponse($response, "Kill request failed for task ID: $taskId");
        } catch (\Exception $e) {
            throw new PrimoApiException("Failed to kill task with ID: $taskId: {$e->getMessage()}");
        }
    }

    protected function createScenarioErrorResponse(Response $response, bool $validation = false): PrimoApiException|PrimoValidationException
    {
        $responseBody = json_decode($response->body(), true);
        $errors = [];

        // Check if 'detail' exists and is an array
        if (isset($responseBody['detail']) && is_array($responseBody['detail']) && ! $validation) {
            foreach ($responseBody['detail'] as $errorDetail) {
                // Ensure 'loc' is an array before using implode
                if (isset($errorDetail['loc']) && is_array($errorDetail['loc'])) {
                    $field = implode(' -> ', $errorDetail['loc']); // Combine loc elements for readability
                } else {
                    $field = $errorDetail['loc'] ?? 'unknown field'; // Fallback if 'loc' is not set or not an array
                }

                // Extract the message
                $message = $errorDetail['msg'] ?? 'unknown error'; // Fallback if 'msg' is not set

                // Add the formatted error to the errors array
                $errors[] = "Field: $field, Message: $message";
            }
        } elseif ($validation) {
            $responseDetail = is_array($responseBody['detail']) ? $responseBody['detail'] : [$responseBody['detail']];
            try {
                $errors = app()->make(DataImportRepository::class)->transformImportColumnErrors($responseDetail);
            } catch (\Exception $e) {
                Log::error('Unable to convert import column errors: '.$e->getMessage());
                $validation = false;
                $errors[] = $responseDetail;
            }
        } else {
            // In case there is no 'detail', add the full response body
            $errors[] = $response->body();
        }

        if ($validation) {
            return new PrimoValidationException(implode('<br>', $errors), $response->status());
        } else {
            // Combine errors into a single string with <br> for line breaks
            return new PrimoApiException(implode('<br>', $errors), $response->status());
        }
    }

    public function uploadDataset(string $path, int $datasetId)
    {
        $response = null;
        try {
            $response = Http::post($this->baseUri.'/data_input_check', [
                'file_path' => config('filesystems.data_upload_directory_path').$path,
                'dataset_id' => $datasetId,
            ]);

            if ($response->ok()) {
                $data = (object) $response->json();

                return $data;
            } elseif ($response->status() == 422) {
                // TODO: Utilize Python Errors
                throw $this->createScenarioErrorResponse($response, true);
            } else {
                throw $this->createScenarioErrorResponse($response);
            }
        } catch (PrimoValidationException $e) {
            throw $e;
        } catch (\Exception $e) {
            Log::error($response);
            throw new PrimoApiException("Dataset upload failed: {$e->getMessage()}");
        }
    }

    public function getAvailableFactors(GeneralSpecifications $data)
    {
        try {
            $response = Http::post($this->baseUri.'/check_for_avail_data', $data);
            if ($response->ok()) {
                $data = (object) $response->json();

                return $data;
            } else {
                throw $this->createScenarioErrorResponse($response);
            }
        } catch (\Exception $e) {
            throw new PrimoApiException("Checking for available factors failed: {$e->getMessage()}");
        }
    }

    public function getKPISummaryInformation(array $data)
    {
        try {
            $response = Http::post($this->baseUri.'/kpi_summary', $data);
            if ($response->ok()) {
                $data = $response->json()['data'];

                return (object) $data;
            } else {
                throw $this->createScenarioErrorResponse($response);
            }
        } catch (\Exception $e) {
            throw new PrimoApiException("Getting KPI Summary Failed: {$e->getMessage()}");
        }
    }
}
