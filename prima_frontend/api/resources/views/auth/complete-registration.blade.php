@extends('layout.layout') @section('title', 'Complete Registration')
@section('content')
<form action="{{ route('password.store') }}" method="POST">
    @csrf
    <div class="flex items-center justify-center flex-col">
        <img src="/images/PRIMO_Logo_official.png" class="logo w-1/4 h-1/4" width="160" height="60" />
        <h1 class="text-2xl text-center">
            To finish setting up your account, please create a password.
        </h1>
    </div>
    <input type="hidden" name="token" value="{{ $token }}" />
    <input type="hidden" name="creation" value="true" />

    <div class="form-input">
        <email-input
            name="email"
            label="Email"
            type="email"
            value="{{ $email ?? old('email') }}"
            model-value="{{ $email ?? old('email') }}"
        ></email-input>
        <div class="error">
            @error('email')
            {{ $message }}
            @enderror
        </div>
    </div>

    <div class="form-input">
        <password-reset></password-reset>
        <div class="error">
            @error('password')
            {{ $message }}
            @enderror
        </div>
    </div>

    @error('success')
    <div class="success">
        {{ $message }}
    </div>
    @enderror @error('error')
    <div class="error">
        {{ $message }}
    </div>
    @enderror
    <br />
    <submit-button label="Create Password"></submit-button>
</form>
@endsection
