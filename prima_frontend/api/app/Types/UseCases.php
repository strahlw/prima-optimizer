<?php

namespace App\Types;

class UseCases
{
    public function __construct(
        public array $cases = []
    ) {
        $this->cases = $cases;
    }
}
