<?php

namespace App\Events;

use App\Http\TaskStatusResponse;
use App\Models\Task;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class TaskFailure
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public Task $task;

    public TaskStatusResponse $taskResponse;

    /**
     * Create a new event instance.
     */
    public function __construct(Task $task, TaskStatusResponse $taskResponse)
    {
        $this->task = $task;
        $this->taskResponse = $taskResponse;
    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return array<int, \Illuminate\Broadcasting\Channel>
     */
    public function broadcastOn(): array
    {
        return [
            new PrivateChannel('user.'.$this->task->user->id),
        ];
    }
}
