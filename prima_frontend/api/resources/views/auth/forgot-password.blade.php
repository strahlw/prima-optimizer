@extends('layout.layout') @section('title', 'Forgot Password')
@section('content')
<form action="{{ route('password.email') }}" method="POST">
    <div class="flex items-center justify-center">
        <img src="/images/PRIMO_Logo_official.png" class="logo w-1/4 h-1/4" width="160" height="60" />
    </div>
    @if (session('status'))
    <div class="success">
        {{ session("status") }} Please follow the instructions in the email to
        reset your password.
    </div>
    <script>
        setTimeout(function () {
            window.close();
        }, 5000); // Close the window after 5 seconds if the reset was successful
    </script>
    @else
    <div class="flex items-center justify-center w-full">
        Forgot your password? Enter your email address to be sent a password
        reset link that will allow you to choose a new one.
    </div>
    <div class="form-input">
        <email-input
            name="email"
            label="Email"
            type="email"
            value=""
        ></email-input>
        <div class="error">
            @error('email')
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
    <submit-button label="Email Password Reset Link"></submit-button>
    @endif
</form>

@endsection
