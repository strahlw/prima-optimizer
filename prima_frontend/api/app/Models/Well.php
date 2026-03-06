<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use MongoDB\Laravel\Eloquent\HybridRelations;
use MongoDB\Laravel\Eloquent\Model;

class Well extends Model
{
    use HasFactory, HybridRelations;

    public $timestamps = false;

    protected $connection = 'mongodb';

    protected $table = 'wells';

    protected $keyType = 'string';

    protected $primaryKey = '_id';

    protected array $keyToLabelArray = [
        'scenario_id' => 'Scenario ID',
        'project_id' => 'Project ID',
        'well_id' => 'Well ID',
        'operator_name' => 'Operator Name',
        'well_priority_score' => 'Well Priority Score',
        'efficiency_score' => 'Efficiency Score',
        'gas' => 'Gas',
        'oil' => 'Oil',
        'age' => 'Age',
        'depth' => 'Depth',
        'latitude' => 'Latitude',
        'longitude' => 'Longitude',
        'incident' => 'Incident',
        'violation' => 'Violation',
        'compliance' => 'Compliance',
        'leak' => 'Leak',
        'schools_within_distance' => 'Schools Within Distance',
        'hospitals_within_distance' => 'Hospitals Within Distance',
        'name' => 'Name',
    ];

    protected $fillable = [
        'scenario_id',
        'well_id',
        'well_rank',
        'priority_score',
        'dataset_json_id',
    ];

    protected function casts(): array
    {
        return [
            'scenario_id' => 'integer',
        ];
    }

    public function projects()
    {
        return Project::whereIn('id', ProjectWell::where('well_id', $this->id)->get()->pluck('project_id')->toArray());
    }

    public function getProjects()
    {
        return Project::whereIn('id', ProjectWell::where('well_id', $this->id)->get()->pluck('project_id')->toArray())->get();
    }

    public function datasetJson(): BelongsTo
    {
        return $this->belongsTo(DatasetJson::class, 'dataset_json_id', 'id');
    }

    protected static function booted()
    {
        // Loading the json data attributes from DatasetJson whenever a well is retrieved
        static::retrieved(function ($well) {
            // Retrieve the related DatasetJson model
            $datasetJson = $well->datasetJson()->first();

            if ($datasetJson) {
                // Merge the json data directly into the Well model's attributes (root level)
                foreach ($datasetJson->json as $key => $value) {
                    // Merge each key-value from json into the root attributes of the Well model
                    $well->$key = $value;
                }
            }
        });
    }

    public function getJsonAttribute()
    {
        return $this->datasetJson?->json;
    }
}
