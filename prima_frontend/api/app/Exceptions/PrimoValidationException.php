<?php

namespace App\Exceptions;

use Exception;
use Illuminate\Support\Facades\Log;

class PrimoValidationException extends Exception
{
    protected string $logChannel = 'api';

    /**
     * Report the exception.
     */
    public function report(): void
    {
        // Log the error to the specified channel
        Log::channel($this->logChannel)->error($this->getMessage());
    }
}
