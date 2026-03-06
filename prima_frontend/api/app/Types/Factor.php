<?php

namespace App\Types;

class Factor
{
    public function __construct(public ?int $value = null, public bool $selected = false) {}
}
