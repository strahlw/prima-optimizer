<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;
use Illuminate\Validation\Rules\Password as RulesPassword;

class ResetPasswordController extends Controller
{
    public function forgotPassword(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
        ]);

        $status = Password::sendResetLink(
            $request->only('email')
        );

        return $status === Password::RESET_LINK_SENT
                    ? back()->with('status', __($status))
                    : back()->withErrors(['email' => __($status)]);
    }

    public function resetPassword(Request $request)
    {
        $request->validate([
            'token' => 'required',
            'email' => 'required|email',
            'password' => ['required', 'confirmed', RulesPassword::defaults()],
        ]);

        $status = Password::reset(
            $request->only('email', 'password', 'password_confirmation', 'token'),
            function (User $user, string $password) {
                $user->forceFill([
                    'password' => Hash::make($password),
                ])->setRememberToken(Str::random(60));

                if (! $user->account_verified) {
                    $user->account_verified = true;
                }

                $user->save();

                event(new PasswordReset($user));
            }
        );

        if ($request->input('creation') === 'true') {
            $frontendUrl = config('app.frontend_url').'/login?creation=true';
        } else {
            $frontendUrl = config('app.frontend_url').'/login?reset=true';
        }

        return $status === Password::PASSWORD_RESET
                    ? redirect()->away($frontendUrl)
                    : back()->withErrors(['email' => [__($status)]]);
    }
}
