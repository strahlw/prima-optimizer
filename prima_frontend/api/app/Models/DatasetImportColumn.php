<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Validation\Rule;

class DatasetImportColumn extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'label',
        'key',
        'required',
        'validation_messages',
        'rules',
        'priority',
        'order',
    ];

    protected function casts(): array
    {
        return [
            'required' => 'boolean',
            'validation_messages' => 'array',
            'rules' => 'array',
        ];
    }

    public function getProcessedValidationRules(): array
    {
        $processedRules = [];
        $requirement = $this->required ? 'required' : 'nullable';
        array_push($processedRules, $requirement);

        foreach ($this->rules as $rule) {
            if (is_string($rule) && strpos($rule, 'in:') === 0) {
                $values = explode(',', substr($rule, 3));
                array_push($processedRules, Rule::in($values));
            } else {
                array_push($processedRules, $rule);
            }
        }

        return $processedRules;
    }
}
