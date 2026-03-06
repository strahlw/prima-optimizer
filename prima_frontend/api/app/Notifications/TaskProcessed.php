<?php

namespace App\Notifications;

use App\Models\Task;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Support\Facades\Log;

class TaskProcessed extends Notification
{
    use Queueable;

    public Task $task;

    /**
     * Create a new notification instance.
     */
    public function __construct(Task $task)
    {
        $this->task = $task;
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
            return (new MailMessage)
                ->subject(config('mail.mail_app_name').": Scenario {$this->task->scenario->data['name']} succeeded")
                ->line("Your recently submitted scenario: {$this->task->scenario->data['name']} has been processed and PRIMO's recommendations are ready for review.")
                ->action('Review Scenario Results', config('app.frontend_url')."/scenarios/{$this->task->scenario->id}")
                ->line('Please review the optimization results and proceed to publish or delete the scenario as needed.')
                ->line('Regards,')
                ->salutation('The '.config('mail.mail_app_name'));
        } catch (\Exception $e) {
            Log::error('TaskProcessed Notification Error: '.$e->getMessage());
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
