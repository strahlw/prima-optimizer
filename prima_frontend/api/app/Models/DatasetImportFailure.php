<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class DatasetImportFailure extends Model
{
    use HasFactory;

    protected $table = 'x_temp_dataset_import_failures';

    public $fillable = [
        'dataset_id',
        'failures',
    ];
}
