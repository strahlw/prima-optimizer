<?php

use App\Http\Middleware\TransformApiRequest;
use App\Http\Middleware\TransformApiResponse;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        // TODO: Assess whether or not "Trust Hosts" is necessary: https://laravel.com/docs/11.x/requests#configuring-trusted-hosts
        // Will most likely have to specify a host in the config files based on the internal network that the frontend would live in.
        $middleware->alias([
            'role' => \Spatie\Permission\Middleware\RoleMiddleware::class,
            'permission' => \Spatie\Permission\Middleware\PermissionMiddleware::class,
            'role_or_permission' => \Spatie\Permission\Middleware\RoleOrPermissionMiddleware::class,
        ]);

        $middleware->prependToGroup('api', [
            TransformApiRequest::class,
            TransformApiResponse::class,
        ]);

        $middleware->prependToGroup('web', [
            TransformApiRequest::class,
            TransformApiResponse::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        //
    })
    ->create();
