@extends('layout.layout') @section('title', 'Login') @section('content')
<form action="{{ route('login.post') }}" method="POST">
    <div class="flex items-center justify-center">
        <img src="/images/prima_official_logo.png" class="logo w-1/4 h-1/4" width="160" height="60" />
    </div>

    @if(request()->query('reset') === 'true')
    <div class="success">
        Your password has been successfully reset. Please use your new password
        to log in.
    </div>
    @endif

    <div class="form-input">
        <email-input
            name="email"
            label="Email"
            type="email"
            value="something@something.com"
        ></email-input>
        <div class="error">
            @error('email')
            {{ $message }}
            @enderror
        </div>
    </div>

    <div class="form-input">
        <password-input
            name="password"
            label="Enter password"
            type="password"
            value="password"
            :feedback="false"
        ></password-input>
        <div class="error">
            @error('password')
            {{ $message }}
            @enderror
        </div>
    </div>
    @csrf @error('success')
    <div class="success">
        {{ $message }}
    </div>
    @enderror @error('error')
    <div class="error">
        {{ $message }}
    </div>
    @enderror
    <br />
    <submit-button label="Continue"></submit-button>
    <br />
    <div class="flex justify-end items-center mt-4">
        <a href="/forgot-password" class="text-primary hover:text-blue-700"
            >Forgot Password?</a
        >
    </div>
</form>
@endsection
