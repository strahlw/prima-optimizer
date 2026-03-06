<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use MongoDB\Laravel\Eloquent\Model;

class DatasetJson extends Model
{
    use HasFactory;

    public $timestamps = false;

    protected $connection = 'mongodb';

    protected $table = 'datasets_json';

    protected $fillable = [
        'json',
        'dataset_id',
    ];

    protected function casts(): array
    {
        return [
            'dataset_id' => 'integer',
        ];
    }

    public function dataset()
    {
        return Dataset::find($this->dataset_id);
    }
}
