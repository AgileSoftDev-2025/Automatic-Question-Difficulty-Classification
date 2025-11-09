// ===================================
// FILE: help.js
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    // ========== FAQ Accordion ==========
    const faqButtons = document.querySelectorAll('.faq-button');

    faqButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Dapatkan panel jawaban (elemen saudara berikutnya)
            const panel = button.nextElementSibling;
            // Dapatkan ikon di dalam tombol
            const icon = button.querySelector('i');

            // Periksa apakah panel ini sedang terbuka
            const isPanelOpen = !panel.classList.contains('hidden');

            // --- Logika untuk menutup semua panel lain ---
            // Ini bersifat opsional, tetapi membuat UI lebih bersih.
            // Hapus baris-baris ini jika Anda ingin beberapa jawaban terbuka sekaligus.
            faqButtons.forEach(otherButton => {
                const otherPanel = otherButton.nextElementSibling;
                const otherIcon = otherButton.querySelector('i');

                // Tutup panel lain dan reset ikonnya
                if (otherButton !== button) {
                    otherPanel.classList.add('hidden'); // Gunakan 'hidden' dari Tailwind
                    otherIcon.classList.remove('bi-dash-circle');
                    otherIcon.classList.add('bi-plus-circle');
                    otherIcon.classList.remove('rotate-180'); // Hapus rotasi jika ada
                }
            });
            // --- Akhir dari logika menutup panel lain ---

            // Buka atau tutup panel yang diklik
            panel.classList.toggle('hidden');

            // Ubah ikon berdasarkan status (terbuka/tertutup)
            if (panel.classList.contains('hidden')) {
                // Panel ditutup
                icon.classList.remove('bi-dash-circle');
                icon.classList.add('bi-plus-circle');
                icon.classList.remove('rotate-180');
            } else {
                // Panel dibuka
                icon.classList.remove('bi-plus-circle');
                icon.classList.add('bi-dash-circle');
                // Anda bisa menambahkan animasi rotasi jika suka
                // icon.classList.add('rotate-180'); 
            }
        });
    });

    // NOTE: Profile dropdown is handled by nav.js
    // Removed duplicate code to prevent conflicts

    console.log('Help page JavaScript loaded successfully');
});