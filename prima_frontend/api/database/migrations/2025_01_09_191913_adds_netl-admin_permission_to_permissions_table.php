<?php

use App\Models\User;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Spatie\Permission\Models\Permission;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('permissions', function (Blueprint $table) {
            $netlAdminPermission = Permission::firstOrCreate(['name' => 'netl-admin', 'guard_name' => 'api']);
            $usersToAdd = User::whereIn('email', [
                'Markus.Drouven@netl.doe.gov',
                'cmcgee_primo@keylogic.com',
                'Hmckinney_primo@keylogic.com',
                'jeremy.langevin+NETL@troyweb.com',
            ]);

            $usersToAdd->each(function ($user) use ($netlAdminPermission) {
                $user->givePermissionTo($netlAdminPermission);
            });
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('permissions', function (Blueprint $table) {
            $permission = Permission::where('name', 'netl-admin')->first();
            DB::table('role_has_permissions')->where('permission_id', $permission->id)->delete();
            $permission->delete();
        });
    }
};
