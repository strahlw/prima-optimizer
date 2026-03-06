<?php

use Illuminate\Support\Facades\Schedule;

Schedule::command('tasks:poll')
    ->everyFiveMinutes()
    ->timezone('America/New_York')
    ->between('6:00', '21:00')
    ->environments(['production', 'staging', 'qa'])
    ->sendOutputTo('/dev/null');

Schedule::command('tasks:send-daily-task-failures')
    ->daily('23:59')
    ->timezone('America/New_York');

Schedule::command('scenarios:delete-old-scenarios')
    ->daily('22:59')
    ->timezone('America/New_York');
