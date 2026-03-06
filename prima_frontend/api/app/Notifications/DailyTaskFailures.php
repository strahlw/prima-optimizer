<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Support\Collection;

class DailyTaskFailures extends Notification
{
    use Queueable;

    public Collection $failedTasks;

    /**
     * Create a new notification instance.
     */
    public function __construct(Collection $failedTasks)
    {
        $this->failedTasks = $failedTasks;
    }

    /**
     * Get the notification's delivery channels.
     *
     * @return array<int, string>
     */
    public function via(object $notifiable): array
    {
        return ['mail'];
    }

    /**
     * Get the mail representation of the notification.
     */
    public function toMail(object $notifiable): MailMessage
    {
        $mailMessage = (new MailMessage)
            ->subject('Daily Task Failures: '.now()->format('m-d-Y'))
            ->line('The following tasks failed throughout the day:');

        $this->failedTasks->each(function ($task) use (&$mailMessage) {
            $mailMessage->line('Task ID: '.$task->task_id.' | Scenario ID: '.$task->scenario_id.' | User: '.$task->scenario->user->first_name.' '.$task->user->last_name);
        });

        return $mailMessage;
    }

    /**
     * Get the array representation of the notification.
     *
     * @return array<string, mixed>
     */
    public function toArray(object $notifiable): array
    {
        return [
            //
        ];
    }
}
