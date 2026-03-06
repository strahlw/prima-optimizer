<?php

namespace App\Exceptions;

use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Illuminate\Support\Facades\App;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;
use Laravel\Passport\Exceptions\OAuthServerException;
use League\OAuth2\Server\Exception\OAuthServerException as ExceptionOAuthServerException;
use Throwable;

class Handler extends ExceptionHandler
{
    protected $dontReport = [
        OAuthServerException::class,
        ExceptionOAuthServerException::class,
    ];

    public function report(Throwable $exception)
    {
        if (str_contains($exception->getMessage(), 'could not be opened in append mode')) {
            // Optionally log a custom message or ignore the exception entirely
            // For example, log a simple message without the full error details
            Log::warning('A logging error occurred: could not open file in append mode.');

            // Return early to prevent further reporting
            return;
        }

        parent::report($exception);

        if (! config('app.debug') && $this->shouldReport($exception)) {
            Mail::raw(
                'Message: '.$exception->getMessage().'<br/>File: '.$exception->getFile().' Line: '.$exception->getLine().'<br/>Stacktrace: '.$exception->getTraceAsString(),
                function ($message) {
                    $message->to(config('mail.exceptions-email.address'), 'NETL QA');
                    $message->subject(strtoupper(config('app.name')).' EXCEPTION IN THE '.strtoupper(App::environment()).' ENVIRONMENT');
                }
            );
        }
    }

    public function render($request, Throwable $exception)
    {
        return parent::render($request, $exception);
    }
}
