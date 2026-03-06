<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class DeleteFile implements ShouldQueue
{
    use Queueable;

    protected $filePath;

    // Constructor to receive file path
    public function __construct($filePath)
    {
        $this->filePath = $filePath;
    }

    // Handle method to delete the file
    public function handle(): void
    {
        try {
            // Perform file deletion
            Storage::delete($this->filePath);
        } catch (\Exception $e) {
            Log::error('Error deleting file: '.$e->getMessage());
        }
    }
}
