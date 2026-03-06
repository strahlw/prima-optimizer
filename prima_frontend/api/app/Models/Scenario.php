<?php

namespace App\Models;

use App\Enum\ScenarioType as EnumScenarioType;
use App\Types\UseCases;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Scenario extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'user_id',
        'organization_id',
        'status',
        'data',
        'dataset_id',
        'status_by_id',
        'parent_id',
        'copy_parent_id',
        'name',
    ];

    protected $appends = [
        'well_count',
        'is_rank_only',
        'is_recommendation_only',
    ];

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'data' => 'array',
            'scenario_id' => 'integer',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    public function projects(): HasMany
    {
        return $this->hasMany(Project::class, 'scenario_id', 'id');
    }

    public function wells()
    {
        // Get project IDs associated with the scenario
        $projectIds = $this->projects()->pluck('id');

        // Get well IDs from the ProjectWell pivot table
        $wellIds = ProjectWell::whereIn('project_id', $projectIds)->pluck('well_id');

        // Fetch wells from MongoDB using the collected well IDs
        return Well::whereIn('id', $wellIds)->get();
    }

    public function getWells()
    {
        return $this->projects->map(function ($project) {
            return $project->getWells();
        })->flatten();
    }

    public function dataset(): BelongsTo
    {
        return $this->belongsTo(Dataset::class);
    }

    public function task(): BelongsTo
    {
        return $this->belongsTo(Task::class, 'id', 'scenario_id');
    }

    public function statusBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'status_by_id');
    }

    public function parent(): BelongsTo
    {
        return $this->belongsTo(Scenario::class, 'parent_id');
    }

    public function copyParent(): BelongsTo
    {
        return $this->belongsTo(Scenario::class, 'copy_parent_id');
    }

    public function getWellCountAttribute(): int
    {
        return Well::where('scenario_id', $this->id)->count();
    }

    public function types(): BelongsToMany
    {
        return $this->belongsToMany(ScenarioType::class, 'scenario_scenario_type')
            ->orderByRaw("FIELD(name, 'Well Ranking', 'P&A Project Recommendations', 'P&A Project Comparisons')");
    }

    public function addTypePivotEntries(array $types): void
    {
        $typeIds = ScenarioType::whereIn('name', $types)->pluck('id');

        $this->types()->syncWithoutDetaching($typeIds);
    }

    public function getIsRankOnlyAttribute(): bool
    {
        return $this->types->count() === 1
            && $this->types->first()->name === EnumScenarioType::WELL_RANKING;
    }

    public function getImpactFactorsAttribute()
    {
        return $this->data['impact_factors'] ?? null;
    }

    public function getEfficiencyFactorsAttribute()
    {
        return $this->data['efficiency_factors'] ?? null;
    }

    public function getIsRecommendationOnlyAttribute(): bool
    {
        return $this->types->count() === 1
            && $this->types->first()->name === EnumScenarioType::PROJECT_RECOMMENDATIONS;
    }

    public function getUseCasesAttribute(): UseCases
    {
        return new UseCases(
            $this->types->pluck('name')->toArray()
        );
    }
}
