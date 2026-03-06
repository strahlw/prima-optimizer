<?php

namespace App\Enum;

class TaskStatus extends Enum
{
    const PENDING = 'PENDING';

    const PROCESSING = 'PROCESSING';

    const FAILURE = 'FAILURE';

    const SUCCESS = 'SUCCESS';

    const KILLED = 'KILLED';
}
