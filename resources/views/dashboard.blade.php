{{-- resources/views/upload.blade.php --}}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-b from-blue-50 to-gray-100 text-gray-900 font-sans">

  {{-- Navbar --}}
  <header class="flex justify-between items-center px-16 py-5 bg-white shadow">
<div class="flex items-center">
    <img src="{{ asset('images/logo.png') }}" alt="Bloomers Logo" class="w-40 h-12">
</div>

<form method="POST" action="{{ route('logout') }}">
    @csrf
    <button type="submit" class="bg-blue-600 text-white px-5 py-2 rounded-md font-semibold hover:bg-blue-700">
        Sign In
    </button>
</form>
  </header>
  {{-- Hero Section --}}
  <section class="px-16 py-16 max-w-4xl">
    <h1 class="text-3xl md:text-4xl font-bold mb-4 leading-snug">
      Smarter <span class="text-blue-600">Question Classification</span><br>with Bloomers
    </h1>
    <p class="text-gray-600 text-base md:text-lg">Automatically analyze question cognitive levels using Bloom's Taxonomy (C1–C6).</p>
  </section>

  {{-- Main Container --}}
  <main class="flex flex-col md:flex-row gap-8 px-16 pb-16">

    {{-- Upload Section --}}
    <div class="flex-1 bg-white p-8 rounded-xl shadow">
      <h2 class="text-lg font-semibold mb-4">Upload Your File</h2>
      <div id="upload-form" class="border-2 border-dashed border-gray-300 rounded-lg p-10 text-center bg-gray-50 transition duration-300">
        <p>Drop your file here or</p>
        <label id="file-label" for="file-input" class="inline-block mt-4 px-6 py-2 bg-blue-600 text-white font-semibold rounded-md cursor-pointer hover:bg-blue-700">
          Upload a file
        </label>
        <input type="file" id="file-input" accept=".csv,.pdf,.txt,.docx" class="hidden">
        <div id="feedback" class="mt-3 text-sm"></div>
        <progress id="progress" value="0" max="100" class="w-full mt-2" hidden></progress>
      </div>
      <button id="classify-btn" class="mt-4 w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">CLASSIFY</button>
    </div>

    {{-- Sidebar --}}
    <aside class="w-full md:w-72 bg-gray-800 text-white p-8 rounded-xl">
      <h3 class="text-blue-400 text-lg font-semibold mb-2">BLOOMERS</h3>
      <p class="font-semibold mb-3">What can you do with Bloomers?</p>
      <ul class="space-y-2 text-sm">
        <li>- Automatically Classify Questions</li>
        <li>- View Your Classification History</li>
        <li>- Adjust or Regenerate Question Levels</li>
        <li>- Everything in one platform</li>
        <li>- View Question Distribution Visualization</li>
        <li>- Download Classification Report</li>
      </ul>
    </aside>

  </main>

  {{-- JS --}}
  <script>
    const dropZone = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const feedback = document.getElementById('feedback');
    const progressBar = document.getElementById('progress');
    const classifyBtn = document.getElementById('classify-btn');
    const MAX_SIZE_MB = 5;

    function formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' bytes';
      else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      else return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function validateFile(file) {
      const allowedTypes = [
        'text/csv',
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      const maxSize = MAX_SIZE_MB * 1024 * 1024;

      if (!allowedTypes.includes(file.type)) {
        feedback.innerHTML = `<span class="text-red-600">Format file tidak didukung. Hanya CSV, PDF, TXT, dan DOCX.</span>`;
        return false;
      }

      if (file.size > maxSize) {
        feedback.innerHTML = `<span class="text-red-600">Ukuran file melebihi ${MAX_SIZE_MB} MB (${formatFileSize(file.size)}).</span>`;
        return false;
      }

      return true;
    }

    async function uploadFile(file) {
      if (!validateFile(file)) return;

      feedback.innerHTML = `Mengunggah <b>${file.name}</b> (${formatFileSize(file.size)})...`;
      progressBar.hidden = false;

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("{{ url('upload') }}", {
          method: "POST",
          body: formData,
          headers: {
            'X-CSRF-TOKEN': '{{ csrf_token() }}'
          }
        });
        const result = await response.json();

        progressBar.hidden = true;

        if (result.success) {
          feedback.innerHTML = `<span class="text-green-600">${result.message}</span>`;
          if (result.result) {
            feedback.innerHTML += `<br><b>Hasil klasifikasi:</b> ${result.result.classification}`;
          }
        } else {
          feedback.innerHTML = `<span class="text-red-600">${result.message}</span>`;
        }
      } catch (error) {
        feedback.innerHTML = `<span class="text-red-600">Terjadi kesalahan saat upload.</span>`;
      }
    }

    classifyBtn.addEventListener('click', () => {
      const file = fileInput.files[0];
      if (file) uploadFile(file);
      else feedback.innerHTML = `<span class="text-red-600">Pilih file terlebih dahulu.</span>`;
    });

    dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      dropZone.classList.add('border-blue-600', 'bg-blue-50');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-blue-600', 'bg-blue-50'));

    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('border-blue-600', 'bg-blue-50');
      const file = e.dataTransfer.files[0];
      if (file) uploadFile(file);
    });
  </script>

</body>
</html>
