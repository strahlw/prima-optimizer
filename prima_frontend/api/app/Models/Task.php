<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

class Task extends Model
{
    use HasFactory;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'task_id',
        'scenario_id',
        'status',
        'status_by_id',
    ];

    /**
     * Get the scenario that owns the task.
     */
    public function scenario(): BelongsTo
    {
        return $this->belongsTo(Scenario::class);
    }

    /**
     * Get the user associated with the task through the scenario.
     */
    public function user(): HasOneThrough
    {
        return $this->hasOneThrough(User::class, Scenario::class, 'id', 'id', 'scenario_id', 'user_id');
    }

    public function statusBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'status_by_id');
    }
}
