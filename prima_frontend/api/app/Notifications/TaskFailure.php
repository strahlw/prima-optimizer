<?php

namespace App\Notifications;

use App\Http\TaskStatusResponse;
use App\Models\Task;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Support\Facades\Log;

class TaskFailure extends Notification
{
    use Queueable;

    protected Task $task;

    protected TaskStatusResponse $taskStatusResponse;

    /**
     * Create a new notification instance.
     */
    public function __construct(Task $task, TaskStatusResponse $taskStatusResponse)
    {
        $this->task = $task;
        $this->taskStatusResponse = $taskStatusResponse;
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
        try {
            // $closingLine = !$this->task->user->hasRole('super-admin') ? 'For assistance in trouble-shooting this issue, please forward this message to primo@netl.doe.gov and povide as much context as possible.' : 'Further details: '.$this->taskStatusResponse->msg;
            $closingLine = 'For assistance in trouble-shooting this issue, please forward this message to primo@netl.doe.gov and povide as much context as possible.';

            return (new MailMessage)
                ->subject(config('mail.mail_app_name').": Scenario {$this->task->scenario->data['name']} failed")
                ->line('Your recently submitted scenario: '.$this->task->scenario->data['name'].' has failed to process.')
                ->line($closingLine)
                ->line('Regards,')
                ->salutation('The '.config('mail.mail_app_name'));
        } catch (\Exception $e) {
            Log::error('TaskFailure Notification Error: '.$e->getMessage());
        }

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
