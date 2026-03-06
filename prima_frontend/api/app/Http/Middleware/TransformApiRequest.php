<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class TransformApiRequest
{
    private function transformKeysToSnakeCase(array $input): array
    {
        $result = [];

        foreach ($input as $key => $value) {
            // Transform the key to snake_case
            $snakeKey = Str::snake($key);

            // If the value is an array, recursively transform its keys
            if (is_array($value)) {
                $result[$snakeKey] = $this->transformKeysToSnakeCase($value);
            } else {
                $result[$snakeKey] = $value;
            }
        }

        return $result;
    }

    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Transform keys of requests that are not GET to snake_case
        if ($request->method() !== 'GET') {
            $input = $request->all();
            $transformedInput = $this->transformKeysToSnakeCase($input);
            $request->replace($transformedInput);
        }

        // Log::info($request->all());

        return $next($request);
    }
}

// Source: https://dev.to/charliet1802/transforming-api-requests-and-responses-in-laravel-11-the-easy-way-21i5#:~:text=As%20you%20may%20know%2C%20snake_case,I%20stuck%20to%20that%20design.\
