<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class DashboardController extends Controller
{
    public function index()
    {
        // bisa kirim data ke dashboard view jika perlu
        return view('dashboard');
    }
}
