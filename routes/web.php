<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Http\Request;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;

// Redirect root ke signin
Route::get('/', function () {
    return redirect()->route('signin');
});

// ===== SIGN IN =====
Route::get('/signin', [AuthController::class, 'showSignIn'])->name('signin');
Route::post('/signin', [AuthController::class, 'login'])->name('signin.post');

// ===== SIGN UP =====
Route::get('/signup', [AuthController::class, 'showSignupForm'])->name('signup');
Route::post('/signup', [AuthController::class, 'register'])->name('register');

// ===== DASHBOARD =====
// Middleware auth agar hanya user login yang bisa mengakses
Route::get('/dashboard', [DashboardController::class, 'index'])
    ->middleware('auth')
    ->name('dashboard');

Route::get('/signin', function () {
    return view('signin.blade.php');
})->name('signin');
