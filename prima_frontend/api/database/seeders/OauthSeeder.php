<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class OauthSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        if (! is_null(DB::table('oauth_clients')->find(config('auth.oauth_client_id')))) {
            return;
        }

        DB::table('oauth_clients')->insert([
            'id' => config('auth.oauth_client_id'),
            'name' => config('app.env'),
            'provider' => 'users',
            'redirect' => config('app.frontend_url').'/auth-redirect',
            'personal_access_client' => 0,
            'password_client' => 0,
            'revoked' => 0,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }
}
