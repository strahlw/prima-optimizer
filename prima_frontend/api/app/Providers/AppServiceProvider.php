<?php

namespace App\Providers;

use App\Models\Passport\Client;
use App\Repositories\DataImportRepository;
use Illuminate\Support\ServiceProvider;
use Illuminate\Validation\Rules\Password;
use Laravel\Passport\Passport;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->bind(\Illuminate\Contracts\Debug\ExceptionHandler::class, \App\Exceptions\Handler::class);
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        Password::defaults(function () {
            $rule = Password::min(8)->letters()->mixedCase()->numbers()->symbols();

            return $rule;
        });
        Passport::useClientModel(Client::class);
        Passport::tokensExpireIn(now()->addMinutes(5));
        Passport::refreshTokensExpireIn(now()->addDays(10));

        HeadingRowFormatter::extend('custom', function ($value, $key) {
            $formattedHeader = app()->make(DataImportRepository::class)->formatHeadingRow($value);

            return ! is_null($formattedHeader) ? $formattedHeader : $key;
        });
    }
}
