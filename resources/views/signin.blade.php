<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sign In - Bloomers</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">

  <div class="flex min-h-screen">
    <!-- Left -->
    <div class="w-1/2 bg-gray-50 flex flex-col justify-center px-24">
    <div class="flex items-center justify-start mb-12">
      <img 
        src="{{ asset('images/logo.png') }}" 
        alt="Bloomers Logo" 
        class="w-49 h-auto object-contain"
      >
    </div>

      <h1 class="text-4xl font-extrabold mb-4 leading-tight">Elevate the Way You <br> Assess</h1>
      <p class="text-gray-600 text-lg">
        Bloomers helps educators streamline question <br>
        analysis with smart AI that classifies cognitive levels <br>
        instantly and objectively.
      </p>
    </div>

    <!-- Right -->
    <div class="w-1/2 bg-gradient-to-b from-indigo-100 to-indigo-200 flex flex-col justify-center items-center">
      <div class="w-2/3">
        <h2 class="text-2xl font-bold text-center mb-8">Welcome Back to Bloomers</h2>

<form action="{{ route('signin.post') }}" method="POST" class="flex flex-col space-y-4">
  @csrf
  <div>
    <label class="block font-medium mb-1">Email</label>
    <input 
      type="email" 
      name="email"
      required
      class="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
  </div>
  <div>
    <label class="block font-medium mb-1">Password</label>
    <input 
      type="password" 
      name="password"
      required
      class="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
  </div>

  <div class="text-right text-sm">
    <a href="#" class="text-blue-600 font-medium hover:underline">Forgot Password?</a>
  </div>

  <button 
    type="submit" 
    class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg shadow">
    Sign In
  </button>

  <p class="text-center mt-4 text-gray-700">
    already have an account? 
    <a href="{{ route('signup') }}" class="text-blue-600 hover:underline font-medium">Sign up here</a>
  </p>
</form>

      </div>
    </div>
  </div>
</body>
</html>
