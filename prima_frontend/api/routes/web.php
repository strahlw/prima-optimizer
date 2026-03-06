<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\ResetPasswordController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('login', function () {
    return view('auth.login');
})->name('login');

Route::get('/forgot-password', function () {
    return view('auth.forgot-password');
})->middleware('guest')->name('password.request');

Route::get('/reset-password/{token}', function (Request $request, string $token) {
    return view('auth.reset-password', ['token' => $token, 'email' => $request->email]);
})->name('password.reset');

Route::get('/complete-registration/{token}', function (Request $request, string $token) {
    return view('auth.complete-registration', ['token' => $token, 'email' => $request->email]);
})->name('password.complete-registration');

Route::post('register', [AuthController::class, 'register'])->name('register.post');
Route::post('login', [AuthController::class, 'login'])->name('login.post');
Route::post('forgot-password', [ResetPasswordController::class, 'forgotPassword'])->middleware('guest')->name('password.email');
Route::post('reset-password', [ResetPasswordController::class, 'resetPassword'])->name('password.store');

Route::fallback(function () {
    return redirect()->away(config('app.frontend_url'));
});
