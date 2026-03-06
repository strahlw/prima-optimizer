<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOne;
use MongoDB\Laravel\Eloquent\HybridRelations;

class Project extends Model
{
    use HasFactory, HybridRelations;

    protected $table = 'projects';

    protected $fillable = [
        'scenario_id',
        'impact_score',
        'efficiency_score',
        'object_id',
        'parent_project_id',
    ];

    protected function casts(): array
    {
        return [
            'scenario_id' => 'integer',
        ];
    }

    public function scenario(): BelongsTo
    {
        return $this->belongsTo(Scenario::class);
    }

    public function wells()
    {
        return Well::whereIn('id', ProjectWell::where('project_id', $this->id)->get()->pluck('well_id')->toArray());
    }

    public function getWells()
    {
        // Add efficiency score as an attribute down the line

        return Well::whereIn('id', ProjectWell::where('project_id', $this->id)->get()
            ->pluck('well_id')->toArray())
            ->get()
            ->map(function (Well $well) {
                $well->efficiency_score = $this->efficiency_score;

                return $well;
            });
    }

    public function getWellCountAttribute()
    {
        return $this->wells()->count();
    }

    public function parent(): HasOne
    {
        return $this->hasOne(Project::class, 'id', 'parent_project_id');
    }

    public function getParentProjectDifferentialsAttribute(): array
    {
        $parent = $this->parent;
        if (! $parent) {
            return [];
        }

        return [
            'impact_score' => $this->impact_score - $parent->impact_score,
            'efficiency_score' => $this->efficiency_score - $parent->efficiency_score,
        ];
    }

    public function getMajorityWellTypeAttribute(): string
    {
        $wellTypes = $this->getWells()->pluck('well_type')->toArray();
        $wellTypeCounts = array_count_values($wellTypes);
        arsort($wellTypeCounts);

        return array_key_first($wellTypeCounts);
    }
}
