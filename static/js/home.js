// --- 1. KODE DRAG/DROP & PREVIEW ANDA ---
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const classifyBtn = document.getElementById("classify-btn");
const filePreview = document.getElementById("file-preview");
const fileNameEl = document.getElementById("file-name");
const removeFileBtn = document.getElementById("remove-file-btn");

function handleFileSelect(file) {
  if (!file) return;
  if (fileNameEl) fileNameEl.textContent = file.name;
  if (filePreview) {
    filePreview.classList.remove("hidden");
    filePreview.classList.add("flex");
  }
  if (dropZone) dropZone.classList.add("hidden");
  if (classifyBtn) classifyBtn.disabled = false;
}

function removeFilePreview() {
  if (fileInput) fileInput.value = "";
  if (filePreview) {
    filePreview.classList.add("hidden");
    filePreview.classList.remove("flex");
  }
  if (dropZone) dropZone.classList.remove("hidden");
  if (classifyBtn) classifyBtn.disabled = true;
}

// Guard akses event listeners jika elemen tidak ada pada halaman
if (removeFileBtn) {
  removeFileBtn.addEventListener("click", removeFilePreview);
}

if (fileInput) {
  fileInput.addEventListener("change", (e) => {
    handleFileSelect(e.target.files[0]);
  });
}

if (dropZone) {
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      () => dropZone.classList.add("border-blue-500", "bg-blue-50"),
      false
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      () => dropZone.classList.remove("border-blue-500", "bg-blue-50"),
      false
    );
  });

  dropZone.addEventListener(
    "drop",
    (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (fileInput) fileInput.files = files;
      handleFileSelect(files[0]);
    },
    false
  );
}

// --- 2. JAVASCRIPT BARU UNTUK DROPDOWN PROFIL ---

// Cek dulu apakah elemennya ada (hanya ada jika user login)
const profileMenuButton = document.getElementById("profile-menu-button");
const profileMenuDropdown = document.getElementById("profile-menu-dropdown");

if (profileMenuButton && profileMenuDropdown) {
  // 1. Tampilkan/sembunyikan dropdown saat tombol diklik
  profileMenuButton.addEventListener("click", () => {
    profileMenuDropdown.classList.toggle("hidden");
  });

  // 2. Sembunyikan dropdown saat pengguna mengklik di luar area dropdown
  window.addEventListener("click", (event) => {
    // Cek apakah target klik BUKAN tombol DAN BUKAN di dalam menu
    if (
      !profileMenuButton.contains(event.target) &&
      !profileMenuDropdown.contains(event.target)
    ) {
      profileMenuDropdown.classList.add("hidden");
    }
  });
}
