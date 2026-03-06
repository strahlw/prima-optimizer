<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\Pivot;
use Illuminate\Database\Eloquent\SoftDeletes;

class ProjectWell extends Pivot
{
    use SoftDeletes;

    protected $connection = 'mysql';

    protected $table = 'project_well';
}
