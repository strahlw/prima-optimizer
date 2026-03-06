<?php

namespace App\Jobs;

use App\Enum\ScenarioStatus;
use App\Enum\TaskStatus;
use App\Events\TaskFailure;
use App\Events\TaskProcessed;
use App\Models\FailedTask;
use App\Models\Task;
use App\Services\PrimoApiService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class PollTask implements ShouldQueue
{
    use Queueable;

    protected Task $task;

    protected PrimoApiService $service;

    /**
     * Create a new job instance.
     */
    public function __construct(Task $task)
    {
        $this->task = $task;
        $this->service = app()->make(PrimoApiService::class);
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        try {
            $this->task->refresh();

            // If task is already processed, don't do anything
            if (in_array($this->task->status, [TaskStatus::SUCCESS, TaskStatus::FAILURE])) {
                Log::debug("Task {$this->task->task_id} already processed with status: {$this->task->status}");

                return;
            }

            Log::debug("Getting task status of task id: {$this->task->task_id}");
            $taskResponse = $this->service->getTaskStatus($this->task->task_id);
            Log::debug("Task status of task id: {$this->task->task_id} is {$taskResponse->status}");
            if ($taskResponse->status === TaskStatus::SUCCESS) {
                try {
                    Log::debug('Updating task and scenario status');
                    DB::beginTransaction();

                    $this->task->update([
                        'status' => TaskStatus::SUCCESS,
                    ]);

                    // Phase 1 - Automatically publish the scenario if the task is successful
                    $this->task->scenario->update([
                        'status' => ScenarioStatus::PUBLISHED,
                    ]);

                    Log::debug('Tasks and status updated, sending processed event');

                    TaskProcessed::dispatch($this->task);

                    DB::commit();
                } catch (\Exception $e) {
                    DB::rollBack();
                    Log::error('Poll task failed for task id: '.$this->task->id.', '.$e->getMessage());
                    Log::error($e->getTraceAsString());
                    throw $e;
                }
            } elseif ($taskResponse->status === TaskStatus::FAILURE) {
                DB::transaction(function () use ($taskResponse) {
                    $updated = DB::table('tasks')
                        ->where('id', $this->task->id)
                        ->where('status', TaskStatus::PENDING)
                        ->update([
                            'status' => TaskStatus::FAILURE,
                            'updated_at' => now(),
                        ]);

                    if ($updated > 0) {
                        $this->task->scenario->update([
                            'status' => ScenarioStatus::FAILURE,
                        ]);

                        FailedTask::create([
                            'task_id' => $this->task->id,
                            'exception' => $taskResponse->msg ?? '',
                        ]);

                        TaskFailure::dispatch($this->task, $taskResponse);
                    }
                });

            } else {
                Log::debug('Task not completed, resending poll task job');
                self::dispatch($this->task)->delay(now()->addMinutes(1));
            }
        } catch (\Exception $e) {
            Log::error('Poll task failed for task id: '.$this->task->id.', '.$e->getMessage());
            Log::error($e->getTraceAsString());
        }

    }
}
