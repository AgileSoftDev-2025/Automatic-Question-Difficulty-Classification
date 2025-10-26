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
    feedback.innerHTML = `<span style="color:red;">Format file tidak didukung. Hanya CSV, PDF, TXT, dan DOCX.</span>`;
    return false;
  }

  if (file.size > maxSize) {
    feedback.innerHTML = `<span style="color:red;">Ukuran file melebihi ${MAX_SIZE_MB} MB (${formatFileSize(file.size)}).</span>`;
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
    const response = await fetch("../../backend/upload.php", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    progressBar.hidden = true;

    if (result.success) {
      feedback.innerHTML = `<span style="color:green;">${result.message}</span>`;

      if (result.result) {
        feedback.innerHTML += `<br><b>Hasil klasifikasi:</b> ${result.result.classification}`;
      }

    } else {
      feedback.innerHTML = `<span style="color:red;">${result.message}</span>`;
    }
  } catch (error) {
    feedback.innerHTML = `<span style="color:red;">Terjadi kesalahan saat upload.</span>`;
  }
}

classifyBtn.addEventListener('click', () => {
  const file = fileInput.files[0];
  if (file) uploadFile(file);
  else feedback.innerHTML = `<span style="color:red;">Pilih file terlebih dahulu.</span>`;
});

dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
});
