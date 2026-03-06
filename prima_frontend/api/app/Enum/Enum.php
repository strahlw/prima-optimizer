<?php

namespace App\Enum;

use Illuminate\Support\Collection;

abstract class Enum
{
    private $enumValue;

    public function __construct($enumValue)
    {
        $this->enumValue = $enumValue;
    }

    public function getValue()
    {
        return $this->enumValue;
    }

    public function getKey()
    {
        return self::search($this->enumValue);
    }

    public function isValid(): bool
    {
        return self::hasValue($this->enumValue);
    }

    public function is($value): bool
    {
        if ($value instanceof self) {
            $value = $value->getValue();
        }

        return $this->enumValue === $value;
    }

    public static function all(): array
    {
        return (new \ReflectionClass(static::class))->getConstants();
    }

    public static function collection(): Collection
    {
        return collect(self::all());
    }

    public static function get($key)
    {
        return self::collection()->get($key);
    }

    public static function values(): array
    {
        return self::collection()->values()->all();
    }

    public static function hasValue($value): bool
    {
        return self::collection()->contains($value);
    }

    public static function keys(): array
    {
        return self::collection()->keys()->all();
    }

    public static function hasKey($key): bool
    {
        return self::collection()->has($key);
    }

    public static function search($value)
    {
        return self::collection()->search($value);
    }

    public static function random()
    {
        return self::collection()->random();
    }
}
