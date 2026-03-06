<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class ScenarioType extends Model
{
    protected $fillable = [
        'name',
    ];

    public function scenarios(): BelongsToMany
    {
        return $this->belongsToMany(Scenario::class, 'scenario_scenario_type');
    }

    public static function getIdByType(string $type): ?int
    {
        return ScenarioType::where('name', $type)->value('id');
    }
}
