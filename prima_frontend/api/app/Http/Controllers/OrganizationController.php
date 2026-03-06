<?php

namespace App\Http\Controllers;

use App\Http\Requests\CreateOrganizationRequest;
use App\Http\Requests\UpdateOrganizationRequest;
use App\Models\Organization;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class OrganizationController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return response()->json(['organizations' => Organization::all()]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateOrganizationRequest $request)
    {
        DB::beginTransaction();
        try {
            $path = null;

            $validated = $request->validated();

            if ($request->hasFile('logo')) {
                // Store the file and get its path
                $path = $validated['logo']->store('organization', 'public');
            }

            $organization = Organization::create([
                'key' => $validated['key'],
                'name' => $validated['name'],
                'logo_path' => $path,
                'available_funding' => $validated['available_funding'],
                'well_count' => $validated['well_count'],
                'pa_target' => $validated['pa_target'],
                'latitude' => $validated['latitude'],
                'longitude' => $validated['longitude'],
            ]);

            DB::commit();

            return response()->json(['message' => 'Organization created.', 'organization' => $organization]);
        } catch (Exception $e) {
            Log::error($e->getMessage());
            DB::rollBack();

            return response()->json(['message' => 'Failed to create organization.', 'error' => $e->getMessage()], 500);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateOrganizationRequest $request, Organization $organization)
    {
        DB::beginTransaction();

        try {
            $path = null;

            $validated = $request->validated();

            $oldLogoPath = null;

            if ($request->hasFile('logo')) {
                // Store the file and get its path
                $oldLogoPath = (string) $organization->logo_path;
                $path = $validated['logo']->store('organization', 'public');
            }

            $updateData = [
                'key' => $validated['key'] ?? $organization->key,
                'name' => $validated['name'] ?? $organization->name,
                'available_funding' => $validated['available_funding'] ?? $organization->available_funding,
                'well_count' => $validated['well_count'] ?? $organization->well_count,
                'pa_target' => $validated['pa_target'] ?? $organization->pa_target,
                'latitude' => $validated['latitude'] ?? $organization->latitude,
                'longitude' => $validated['longitude'] ?? $organization->longitude,
            ];

            if ($path) {
                $updateData['logo_path'] = $path;
            }

            $organization->update($updateData);

            if ($oldLogoPath) {
                // Delete the old logo
                Storage::delete('public/'.$oldLogoPath);
            }

            DB::commit();

            return response()->json(['message' => 'Organization updated.', 'organization' => $organization]);
        } catch (Exception $e) {
            Log::error($e->getMessage());
            DB::rollBack();

            return response()->json(['message' => 'Failed to update organization.', 'error' => $e->getMessage()], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Request $request, Organization $organization)
    {
        if (! $request->user()->can('delete', $organization)) {
            return response()->json(['message' => 'Unauthorized to delete organizations.'], 403);
        }

        $organization->delete();

        return response()->json(['message' => 'Organization deleted.', 'id' => $organization->id]);
    }
}
