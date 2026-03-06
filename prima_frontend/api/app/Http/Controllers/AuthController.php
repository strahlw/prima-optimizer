<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Password;
use Laravel\Passport\RefreshTokenRepository;
use Laravel\Passport\TokenRepository;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $validated = $request->validate([
            'email' => ['bail', 'required', 'exists:users,email'],
            'password' => ['bail', 'required', 'string'],
        ]);

        if (auth()->attempt($validated)) {
            return redirect()->intended();
        }

        return back()->withErrors(['error' => 'Invalid username or password']);
    }

    public function logout(Request $request)
    {
        [$headerEncoded, $payloadEncoded, $signatureEncoded] = explode('.', $request->bearerToken());
        $payloadJson = base64_decode(strtr($payloadEncoded, '-_', '+/'));
        $decoded = json_decode($payloadJson);

        $accessToken = app()->make(TokenRepository::class)->findForUser($decoded->jti, User::find($decoded->sub)->getAuthIdentifier());

        if (is_null($accessToken)) {
            return response()->json(['message' => 'Token not found'], 404);
        }

        $accessToken->revoke();

        app()->make(RefreshTokenRepository::class)->revokeRefreshTokensByAccessTokenId($accessToken->id);

        return response()->json(['message' => 'Logged out successfully']);
    }

    public function resendAccountCreationEmail(Request $request, User $user)
    {
        $admin = $request->user();

        if (! $admin->hasRole('super-admin') && ($admin->hasRole('org-admin') && $admin->organization_id !== $user->organization_id)) {
            return response()->json(['message' => 'Unauthorized to create users outside your organization'], 401);
        }

        if ($user->account_verified) {
            return response()->json(['message' => 'User account is already verified'], 400);
        }

        try {
            // Customize the broker to allow for 24 hour reset expiration.
            $broker = Password::broker('users_welcome');

            $status = $broker->sendResetLink(
                ['email' => $user->email],
            );

            if ($status === Password::RESET_LINK_SENT) {
                // Return success response as JSON
                return response()->json(['message' => 'Account creation email resent successfully'], 200);
            } else {
                // Return error response for failed email link
                return response()->json(['message' => __($status)], 400);
            }
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Failed to resend account creation link.'], 500);
        }
    }

    public function hideDisclaimer(Request $request)
    {
        $user = $request->user();

        try {
            $user->update(['show_disclaimer' => false]);

            return response()->json(['message' => 'Saved disclaimer visibility preference'], 200);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Failed to save disclaimer preference'], 500);
        }
    }
}
