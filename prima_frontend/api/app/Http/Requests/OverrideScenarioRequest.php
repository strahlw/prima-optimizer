<?php

namespace App\Http\Requests;

use App\Exceptions\OverrideScenarioValidationException;
use App\Models\Project;
use App\Models\ProjectWell;
use App\Models\Well;
use App\Types\ScenarioOverrideData;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class OverrideScenarioRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'name' => ['string', 'required', Rule::unique('scenarios', 'name')->where(function ($query) {
                return $query->where('organization_id', $this->route('scenario')->organization_id);
            }), ],
            'projects_remove' => ['array'],
            'wells_remove' => ['array'],
            'projects_lock' => ['array'], // Should validate this exists in projects.
            'wells_lock' => ['array'], // Should validate this exists in wells.
            'wells_reassign_from' => ['array'],
            'wells_reassign_to' => ['array'],
        ];
    }

    // Validate and convert
    public function convertToOverrideData(): ScenarioOverrideData
    {
        $name = $this->input('name');
        $projectsRemove = $this->input('projects_remove', []);
        $wellsRemove = $this->input('wells_remove', []);
        $projectsLock = $this->input('projects_lock', []);
        $wellsLock = $this->input('wells_lock', []);
        $wellsReassignFrom = $this->input('wells_reassign_from', []);
        $wellsReassignTo = $this->input('wells_reassign_to', []);

        if ($projectsRemove) {
            $projectsRemoveProjects = Project::whereIn('id', $projectsRemove);
            if ($projectsRemoveProjects->get()->isNotEmpty() && count($projectsRemove) !== $projectsRemoveProjects->count()) {
                throw new OverrideScenarioValidationException('One or more projects to remove do not exist.');
            }
        }

        if ($wellsRemove) {
            $projectIds = array_keys($wellsRemove);

            if (count($projectIds) !== Project::whereIn('id', $projectIds)->count()) {
                throw new OverrideScenarioValidationException('One or more projects to remove wells from do not exist.');
            }

            $wellIds = collect($wellsRemove)->flatMap(function ($wells) {
                return $wells;
            })->pluck('id')->toArray();

            if (count($wellIds) !== Well::whereIn('id', $wellIds)->get()->pluck('id')->unique()->count()) {
                throw new OverrideScenarioValidationException('One or more wells to remove do not exist.');
            }
        }

        if ($projectsLock) {
            if (count($projectsLock) !== Project::whereIn('id', $projectsLock)->count()) {
                throw new OverrideScenarioValidationException('One or more projects to remove do not exist.');
            }
        }

        if ($wellsLock) {
        }

        if ($wellsReassignFrom) {
            $wellIds = collect($wellsReassignFrom)->pluck('id')->toArray();

            if (count($wellIds) !== Well::whereIn('id', $wellIds)->get()->pluck('id')->unique()->count()) {
                throw new OverrideScenarioValidationException('One or more wells to reassign from do not exist.');
            }
        }

        // TODO: This validation will need to change with the idea of a "default" project / creating new projects
        if ($wellsReassignTo) {
            $projectIds = array_keys($wellsReassignTo);

            if (count($projectIds) !== Project::whereIn('id', $projectIds)->count()) {
                throw new OverrideScenarioValidationException('One or more projects to reassign to do not exist.');
            }

            $wellIds = collect($wellsReassignTo)->flatMap(function ($wells, $projectId) {
                return collect($wells)->filter(function ($well) use ($projectId) {
                    // Check if the well was previously assigned to a project for existing wells
                    return ProjectWell::where('well_id', $well['well_id'])->where('project_id', $projectId)->exists();
                });
            })->pluck('id')->toArray();

            // Currently not checking dataset_jsons
            if (count($wellIds) !== Well::whereIn('id', $wellIds)->get()->pluck('id')->unique()->count()) {
                throw new OverrideScenarioValidationException('One or more wells to reassign do not exist.');
            }
        }

        $projectsRemove = isset($projectsRemoveProjects) ? $projectsRemoveProjects->pluck('id')->toArray() : [];

        $wellsRemove = collect($wellsRemove)->mapWithKeys(function ($wells, $projectId) {
            return [$projectId => collect($wells)->pluck('id')->toArray()];
        })->toArray();
        $wellsReassignFrom = [];
        $wellsReassignTo = collect($wellsReassignTo)->mapWithKeys(function ($wells, $projectId) {
            return [$projectId => collect($wells)->pluck('well_id')->toArray()];
        })->toArray();

        return new ScenarioOverrideData(
            $name,
            $projectsRemove,
            $wellsRemove,
            $projectsLock,
            $wellsLock,
            $wellsReassignFrom,
            $wellsReassignTo
        );
    }

    public function messages()
    {
        return ['name.unique' => 'The name used for an override scenario must be unique'];
    }
}
