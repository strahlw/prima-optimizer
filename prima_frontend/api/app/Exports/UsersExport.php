<?php

namespace App\Exports;

use App\Models\User;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;

class UsersExport implements FromCollection, WithHeadings
{
    public function headings(): array
    {
        return [
            'Name', 'FirstName', 'LastName', 'ExternalEmailAddress', 'Company', 'Department',
        ];
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        return User::all()->map(function ($user) {
            return [$user->first_name.' '.$user->last_name, $user->first_name, $user->last_name, $user->email, $user->organization?->key ?? '', ''];
        });
    }
}
