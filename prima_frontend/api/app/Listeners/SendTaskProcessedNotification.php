<?php

namespace App\Listeners;

use App\Events\TaskProcessed;
use App\Notifications\TaskProcessed as NotificationsTaskProcessed;

class SendTaskProcessedNotification
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
    public function handle(TaskProcessed $event): void
    {
        $event->task->user->notify(new NotificationsTaskProcessed($event->task));
    }
}
