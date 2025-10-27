<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Auth;

class AuthController extends Controller
{
    // 🔹 Tampilkan halaman Sign Up
    public function showSignupForm()
    {
        return view('signup');
    }

    // 🔹 Proses pendaftaran akun baru
    public function register(Request $request)
    {
        $request->validate([
            'username' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:6',
        ]);

        // Simpan user ke database
        User::create([
            'name' => $request->username,
            'email' => $request->email,
            'password' => Hash::make($request->password),
        ]);

        // Redirect ke Sign In dengan pesan sukses
        return redirect()->route('signin')->with('success', 'Account created successfully! Please sign in.');
    }

    // 🔹 Tampilkan halaman Sign In
    public function showSignIn()
    {
        return view('signin');
    }

    // 🔹 Proses login user
    public function login(Request $request)
    {
        $credentials = $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        // Coba login
        if (Auth::attempt($credentials)) {
            $request->session()->regenerate();
            return redirect()->intended('/dashboard'); // ganti sesuai dashboardmu
        }

        // Jika gagal login
        return back()->withErrors([
            'login_error' => 'Email atau password salah. Silakan coba lagi.',
        ])->onlyInput('email'); // email tetap tersimpan
    }

    // 🔹 Logout user
    public function logout(Request $request)
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('signin')->with('success', 'You have been logged out.');
    }
}
