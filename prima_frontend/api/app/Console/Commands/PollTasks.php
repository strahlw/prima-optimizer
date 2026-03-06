<?php

namespace App\Console\Commands;

use App\Enum\TaskStatus;
use App\Jobs\PollTask;
use App\Models\Task;
use App\Services\PrimoApiService;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

class PollTasks extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'tasks:poll {task_id?}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Poll the Primo API for task status updates';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        try {
            app()->make(PrimoApiService::class)->verifyConnection();

            if ($this->argument('task_id')) {
                $task = Task::firstWhere('task_id', $this->argument('task_id'));
                if ($task) {
                    Log::debug("Polling task with ID: {$task->task_id}");
                    PollTask::dispatch($task);
                } else {
                    $this->error('Task not found');
                }
            } else {
                Task::whereIn('status', [TaskStatus::PENDING, TaskStatus::PROCESSING])
                    ->chunk(50, function ($tasks) {
                        $tasks->each(function (Task $task) {
                            Log::debug("Polling task with ID: {$task->task_id}");
                            PollTask::dispatch($task);
                        });
                    });
            }
        } catch (\Exception $e) {
            Log::error('An Exception occured in the Poll Tasks command');
            Log::debug($e->getMessage());
            $this->error($e->getMessage());
        }
    }
}
