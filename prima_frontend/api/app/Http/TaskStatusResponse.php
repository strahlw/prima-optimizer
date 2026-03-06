<?php

namespace App\Http;

use Carbon\Carbon;

class TaskStatusResponse
{
    public string $taskId;

    public string $status;

    public Carbon $date;

    public string $msg;

    public function __construct(string $taskId, string $status, string $date, string $msg = '')
    {
        $this->taskId = $taskId;
        $this->status = $status;
        $this->date = Carbon::parse($date);
        $this->msg = $msg;
    }
}
