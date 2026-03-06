<?php

namespace App\Listeners;

use App\Events\TaskFailure;
use App\Notifications\TaskFailure as NotificationsTaskFailure;

class SendTaskFailureNotification
{
    /**
     * Create the event listener.
     */
    public function __construct()
    {
        //
    }

    /**
     * Handle the event.
     */
    public function handle(TaskFailure $event): void
    {
        $event->task->user->notify(new NotificationsTaskFailure($event->task, $event->taskResponse));
    }
}
