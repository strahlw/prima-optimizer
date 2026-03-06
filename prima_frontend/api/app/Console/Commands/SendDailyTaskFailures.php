<?php

namespace App\Console\Commands;

use App\Enum\TaskStatus;
use App\Models\Task;
use App\Models\User;
use App\Notifications\DailyTaskFailures;
use Illuminate\Console\Command;

class SendDailyTaskFailures extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'tasks:send-daily-task-failures';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'At the end of each day, collect any tasks that failed during the day and send them to the admins.';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        $failedTasks = Task::where('status', TaskStatus::FAILURE)
            ->whereDate('updated_at', now())
            ->get();

        if ($failedTasks->count() === 0) {
            $this->info('No failed tasks to report.');

            return;
        }

        try {
            collect(config('mail.task_email_admins'))->each(function ($email) use ($failedTasks) {
                $user = User::where('email', $email)->first();
                if ($user) {
                    $user->notify(new DailyTaskFailures($failedTasks));
                }
            });

            $this->info('Daily task failures have been reported.');
        } catch (\Exception $e) {
            $this->error('An error occurred while sending the daily task failures: '.$e->getMessage());
        }

    }
}
