const dropZone = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const feedback = document.getElementById('feedback');
const progressBar = document.getElementById('progress');
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

function simulateUpload(file) {
  progressBar.hidden = false;
  feedback.innerHTML = `Mengunggah <b>${file.name}</b> (${formatFileSize(file.size)})...`;
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.value = progress;
    if (progress >= 100) {
      clearInterval(interval);
      feedback.innerHTML = `<span style="color:green;">File <b>${file.name}</b> berhasil diunggah!</span>`;
      progressBar.hidden = true;
    }
  }, 200);
}

fileInput.addEventListener('change', e => {
  const file = e.target.files[0];
  if (file && validateFile(file)) simulateUpload(file);
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
  if (file && validateFile(file)) simulateUpload(file);
});
