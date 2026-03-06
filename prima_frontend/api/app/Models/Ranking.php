<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use MongoDB\Laravel\Eloquent\Model;

class Ranking extends Model
{
    use HasFactory;

    protected $connection = 'mongodb';

    protected $table = 'ranked_wells';

    protected $fillable = [
        'dataset_json_id',
    ];

    public function datasetJson(): BelongsTo
    {
        return $this->belongsTo(DatasetJson::class, 'dataset_json_id', 'id');
    }

    public function getJsonAttribute()
    {
        return $this->datasetJson?->json;
    }
}
