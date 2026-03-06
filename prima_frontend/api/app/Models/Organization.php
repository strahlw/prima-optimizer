<?php

namespace App\Models;

use App\Casts\TrimTrailingZerosCast;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Support\Facades\Storage;

class Organization extends Model
{
    use HasFactory, SoftDeletes;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'key',
        'name',
        'logo_path',
        'available_funding',
        'well_count',
        'pa_target',
        'latitude',
        'longitude',
    ];

    protected $appends = ['logo_url'];

    protected function casts(): array
    {
        return [
            'longitude' => TrimTrailingZerosCast::class,
            'latitude' => TrimTrailingZerosCast::class,
        ];
    }

    public function users(): HasMany
    {
        return $this->hasMany(User::class);
    }

    public function datasets(): HasMany
    {
        return $this->hasMany(Dataset::class);
    }

    public function getLogoUrlAttribute()
    {
        // Check if logo_path is not null and exists
        if ($this->logo_path && Storage::disk('public')->exists($this->logo_path)) {
            return asset('storage/'.$this->logo_path);
        }

        // Return a default image URL or an empty string if the file doesn't exist
        return null;
    }
}
