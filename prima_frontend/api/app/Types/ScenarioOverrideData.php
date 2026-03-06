<?php

namespace App\Types;

class ScenarioOverrideData
{
    public string $name;

    public array $projects_remove;

    public array $wells_remove;

    public array $projects_lock;

    public array $wells_lock;

    public array $wells_reassign_from;

    public array $wells_reassign_to;

    public function __construct(
        string $name,
        array $projects_remove,
        array $wells_remove,
        array $projects_lock,
        array $wells_lock,
        array $wells_reassign_from,
        array $wells_reassign_to
    ) {
        $this->name = $name;
        $this->projects_remove = $projects_remove;
        $this->wells_remove = $wells_remove;
        $this->projects_lock = $projects_lock;
        $this->wells_lock = $wells_lock;
        $this->wells_reassign_from = $wells_reassign_from;
        $this->wells_reassign_to = $wells_reassign_to;
    }
}
