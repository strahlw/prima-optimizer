<?php

namespace App\Enum;

class ScenarioStatus extends Enum
{
    const PUBLISHED = 'Published';

    const IN_REVIEW = 'In Review';

    const PROCESSING = 'Processing';

    const FAILURE = 'Failure';

    const KILLED = 'Killed';
}
