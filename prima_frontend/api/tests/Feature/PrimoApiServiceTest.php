<?php

use App\Enum\TaskStatus;
use App\Exceptions\PrimoApiException;
use App\Http\TaskStatusResponse;
use App\Services\PrimoApiService;
use Carbon\Carbon;
use Illuminate\Support\Facades\Http;

beforeEach(function () {
    $this->service = app()->make(PrimoApiService::class);
});

test('verifyConnection returns true on a 200 status code', function () {
    Http::fake([
        config('app.python_api_url').'/ping' => Http::response('', 200),
    ]);

    expect($this->service->verifyConnection())->toBeTrue();
});

test('verifyConnection throws an exception on any non-200 status code', function () {
    Http::fake([
        config('app.python_api_url').'/ping' => Http::response('', 500),
    ]);

    expect(fn () => $this->service->verifyConnection())->toThrow(PrimoApiException::class);
});

test('getTaskStatus returns a TaskStatusResponse after a successful request', function () {
    Http::fake([
        config('app.python_api_url').'/status/1' => Http::response(['id' => 1, 'status' => TaskStatus::PENDING, 'date' => now()->toString()], 200),
    ]);

    $resource = $this->service->getTaskStatus(1);
    expect($resource)->toBeInstanceOf(TaskStatusResponse::class);
    expect($resource->taskId)->toBe(1);
    expect($resource->status)->toBe(TaskStatus::PENDING);
    expect($resource->date)->toBeInstanceOf(Carbon::class);
});

// test('getTaskStatus throws a PrimoApiException after a 422 request', function () {
//     // TODO: Verify structure of detail object
//     Http::fake([
//         config('app.python_api_url').'/status/1' => Http::response([], 422),
//     ]);

//     expect($this->service->getTaskStatus(1))->toThrow(PrimoApiException::class);
// });
