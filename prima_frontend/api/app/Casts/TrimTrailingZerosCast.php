<?php

namespace App\Casts;

use Illuminate\Contracts\Database\Eloquent\CastsAttributes;

class TrimTrailingZerosCast implements CastsAttributes
{
    /**
     * Cast the given value when retrieved from the database.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @param  string  $key
     * @param  mixed  $value
     * @param  array  $attributes
     * @return string
     */
    public function get($model, $key, $value, $attributes)
    {
        // Trim trailing zeros from the decimal value
        return rtrim(rtrim($value, '0'), '.');
    }

    /**
     * Prepare the value for storage in the database.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @param  string  $key
     * @param  mixed  $value
     * @param  array  $attributes
     * @return string
     */
    public function set($model, $key, $value, $attributes)
    {
        // Return the value as is for storage
        return $value;
    }
}
