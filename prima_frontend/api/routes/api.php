<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\DatasetController;
use App\Http\Controllers\ExportController;
use App\Http\Controllers\KPISummaryController;
use App\Http\Controllers\OrganizationController;
use App\Http\Controllers\RoleController;
use App\Http\Controllers\ScenarioController;
use App\Http\Controllers\UserController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:api');

Route::prefix('role')->group(function () {
    Route::get('/', [RoleController::class, 'index'])->name('role.index');
});

Route::get('/roles-and-permissions', function (Request $request) {
    return response()->json(['role' => $request->user()->roleName, 'permissions' => $request->user()->permission_names, 'organization' => $request->user()->organization, 'user' => $request->user()->append('roleId')]);
})->middleware('auth:api')->name('getRolesAndPermissions');

Route::post('/logout', [AuthController::class, 'logout']);
Route::post('/resend-account-creation-email/{user}', [AuthController::class, 'resendAccountCreationEmail'])->middleware(['auth:api', 'permission:add-users'])->name('resend-account-creation-email');
Route::post('/hide-disclaimer', [AuthController::class, 'hideDisclaimer'])->middleware('auth:api')->name('hide-disclaimer');

Route::prefix('user')->middleware('auth:api')->group(function () {
    Route::get('/supers')->uses([UserController::class, 'getSuperAdmins'])->name('user.get-supers');
    Route::get('/{organization}', [UserController::class, 'getOrganizationUsers'])->name('user.get-organization-users');
    Route::post('/', [UserController::class, 'store'])->name('user.create')->middleware('permission:add-users');
    Route::put('/{user}', [UserController::class, 'update'])->name('user.update');
    Route::delete('/{user}', [UserController::class, 'destroy'])->name('user.delete')->middleware('permission:delete-users');
});

Route::prefix('dataset')->middleware('auth:api')->group(function () {
    Route::get('/template', [DatasetController::class, 'getTemplate'])->name('dataset.get-template');
    Route::get('/', [DatasetController::class, 'index'])->name('dataset.index');
    Route::get('/{dataset}', [DatasetController::class, 'show'])->name('dataset.show');
    Route::post('/upload', [DatasetController::class, 'store'])->name('dataset.store')->middleware('permission:upload-data');
});

Route::prefix('project')->middleware('auth:api')->group(function () {
    Route::get('wells/{projectId}', [ScenarioController::class, 'getProjectWells'])->name('project.get-project-wells');
});

Route::prefix('scenario')->middleware('auth:api')->group(function () {
    Route::get('/', [ScenarioController::class, 'index'])->name('scenario-review.index');
    Route::post('/', [ScenarioController::class, 'store'])->name('scenario.store');
    Route::post('/rankOnly', [ScenarioController::class, 'storeRankOnly'])->name('scenario.store-rank-only');
    Route::post('/{scenario}/rank', [ScenarioController::class, 'rankExistingScenario'])->name('scenario.get-scenario-ranked-data');
    Route::post('/rank', [ScenarioController::class, 'rank'])->name('scenario.rank');
    Route::get('/rank/{taskId}', [ScenarioController::class, 'getRankingData'])->name('rank.get-ranked-data');
    Route::delete('/rank/{taskId}', [ScenarioController::class, 'deleteRankingData'])->name('rank.delete-ranked-data');
    Route::put('/{scenario}/rename', [ScenarioController::class, 'updateName'])->name('scenario.rename');
    Route::get('/{scenario}/params', [ScenarioController::class, 'getScenarioParams'])->name('scenario.get-scenario-params');
    Route::post('/available-factors', [ScenarioController::class, 'getAvailableFactors'])->name('scenario.available-factors');
    Route::get('/{scenario}/kpi-summary', KPISummaryController::class)->name('scenario.kpi-summary');

    Route::get('/published', [ScenarioController::class, 'getPublishedScenarios'])->name('scenario.get-published-scenarios');
    Route::post('publish/{scenario}', [ScenarioController::class, 'publish'])->name('scenario.publish');
    Route::delete('delete/{scenario}', [ScenarioController::class, 'destroy'])->name('scenario.delete');
    Route::put('kill/{scenario}', [ScenarioController::class, 'kill'])->name('scenario.kill-optimization');
    Route::get('projects/{scenario}', [ScenarioController::class, 'getProjects'])->name('scenario.get-projects');
    Route::post('wells/{scenario}/search', [ScenarioController::class, 'searchAvailableWells'])->name('scenario.search-available-wells');
    Route::post('override/{scenario}', [ScenarioController::class, 'override'])->name('scenario.override');
    Route::get('initial-visible-wells', [ScenarioController::class, 'getInitialVisibleWells'])->name('scenario.get-initial-visible-wells');
    Route::get('/check-name', [ScenarioController::class, 'checkName'])->name('scenario.check-name');
});

Route::prefix('export')->middleware('auth:api')->group(function () {
    Route::post('/ranked-wells', [ExportController::class, 'exportRankedData'])->name('export.ranked-data');
    Route::post('/raw-data', [ExportController::class, 'exportRawData'])->name('export.raw-data');
    Route::post('/download-projects', [ExportController::class, 'downloadProjects'])->name('export.projects');
    Route::get('/user-list', [ExportController::class, 'exportUserList'])->name('export.user-list');
    Route::post('/scenario-ranking/{scenario}', [ExportController::class, 'exportScenarioRanking'])->name('export.scenario-ranking');
});

Route::get('organizations', [OrganizationController::class, 'index'])->name('get.organizations');

Route::prefix('organization')->middleware('auth:api', 'role:super-admin')->group(function () {
    Route::post('/', [OrganizationController::class, 'store'])->name('organization.create');
    Route::post('/{organization}', [OrganizationController::class, 'update'])->name('organization.update');
    Route::delete('/{organization}', [OrganizationController::class, 'destroy'])->name('organization.delete');
});
