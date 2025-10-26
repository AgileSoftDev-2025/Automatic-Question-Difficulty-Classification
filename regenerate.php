<?php

/**
 * Fungsi untuk mengekstrak kata kunci dari sebuah kalimat.
 * Ini adalah versi sederhana. Untuk hasil yang lebih baik, diperlukan algoritma NLP yang lebih kompleks.
 *
 * @param string $question Kalimat soal asli.
 * @return array Asosiatif berisi 'keyword' dan 'context'.
 */
function extract_keywords($question) {
    // Menghapus kata-kata umum (stopwords) dan kata kerja perintah
    $stopwords = [
        'jelaskan', 'sebutkan', 'apa', 'yang', 'dimaksud', 'dengan', 'dalam', 'proses', 
        'secara', 'singkat', 'adalah', 'uraikan', 'analisis', 'buatlah'
    ];

    // Membersihkan soal dari stopwords
    $clean_question = str_ireplace($stopwords, '', $question);
    $clean_question = trim(preg_replace('/\s+/', ' ', $clean_question));

    // Mencoba menemukan frasa yang ditulis dengan huruf kapital (seperti "User Persona")
    preg_match_all('/\b[A-Z][a-zA-Z]*\s[A-Z][a-zA-Z]*\b/', $question, $matches);

    if (!empty($matches[0])) {
        // Jika ditemukan frasa seperti "User Persona"
        $keyword = $matches[0][0];
        $context = trim(str_ireplace($keyword, '', $clean_question));
    } else {
        // Jika tidak, gunakan logika sederhana: kata pertama sebagai keyword, sisanya konteks
        $words = explode(' ', $clean_question);
        $keyword = array_shift($words);
        $context = implode(' ', $words);
    }

    return [
        'keyword' => $keyword,
        'context' => !empty($context) ? $context : $keyword // fallback jika context kosong
    ];
}


/**
 * Fungsi utama untuk meregenerasi soal.
 *
 * @param string $original_question Soal asli.
 * @param string $target_level Level kognitif yang dituju (e.g., 'C4').
 * @return string Soal baru yang sudah diregenerasi.
 */
function regenerate_question($original_question, $target_level) {
    // Definisikan template untuk setiap level Taksonomi Bloom
    $templates = [
        'C1' => ["Sebutkan definisi dari [KEYWORD].", "Apa yang dimaksud dengan [KEYWORD] dalam konteks [CONTEXT]?"],
        'C2' => ["Jelaskan [KEYWORD] dengan menggunakan bahasamu sendiri.", "Bandingkan antara [KEYWORD] dengan konsep lain yang relevan dalam [CONTEXT]."],
        'C3' => ["Berikan sebuah contoh konkret penerapan [KEYWORD] dalam situasi [CONTEXT].", "Bagaimana Anda akan menggunakan konsep [KEYWORD] untuk menyelesaikan sebuah masalah?"],
        'C4' => ["Analisis komponen-komponen utama yang membentuk [KEYWORD].", "Identifikasi kelebihan dan kekurangan dari [KEYWORD] saat diterapkan pada [CONTEXT]."],
        'C5' => ["Menurut pendapat Anda, seberapa efektif penggunaan [KEYWORD] dalam [CONTEXT]? Berikan justifikasi untuk argumen Anda.", "Evaluasilah dampak positif dan negatif dari penerapan [KEYWORD]."],
        'C6' => ["Rancanglah sebuah metode baru yang terinspirasi oleh [KEYWORD] untuk meningkatkan [CONTEXT].", "Buatlah sebuah kerangka kerja untuk mengimplementasikan [KEYWORD] secara efektif."]
    ];

    // Pastikan level target ada di dalam template
    if (!isset($templates[$target_level])) {
        return "Error: Level target tidak valid.";
    }

    // 1. Ekstrak kata kunci dari soal asli
    $extracted = extract_keywords($original_question);
    $keyword = $extracted['keyword'];
    $context = $extracted['context'];

    // 2. Pilih salah satu template secara acak dari level yang dituju
    $available_templates = $templates[$target_level];
    $chosen_template = $available_templates[array_rand($available_templates)];

    // 3. Ganti placeholder [KEYWORD] dan [CONTEXT] dengan hasil ekstraksi
    $new_question = str_replace('[KEYWORD]', $keyword, $chosen_template);
    $new_question = str_replace('[CONTEXT]', $context, $new_question);

    return $new_question;
}


// --- Main Logic ---
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $original_question = $_POST['original_question'];
    $initial_level = $_POST['initial_level'];
    $target_level = $_POST['target_level'];

    // Panggil fungsi regenerasi
    $new_question = regenerate_question($original_question, $target_level);
} else {
    // Jika diakses langsung, redirect ke halaman form
    header('Location: index.php');
    exit();
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hasil Regenerasi Soal</title>
    <style>
        body { font-family: sans-serif; max-width: 700px; margin: 40px auto; background-color: #f4f4f9; color: #333; }
        .container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #007bff; }
        .result-box { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; background-color: #fafafa; }
        .result-box h4 { margin-top: 0; color: #333; }
        .new-question-box { background-color: #e7f5ff; }
        a { display: inline-block; margin-top: 20px; text-decoration: none; padding: 10px 20px; background-color: #007bff; color: white; border-radius: 4px; }
        a:hover { background-color: #0056b3; }
    </style>
</head>
<body>

<div class="container">
    <h2>✅ Hasil Regenerasi Soal</h2>

    <div class="result-box">
        <h4>Soal Asli (Level: <?php echo htmlspecialchars($initial_level); ?>)</h4>
        <p><?php echo htmlspecialchars($original_question); ?></p>
    </div>

    <div class="result-box new-question-box">
        <h4>Soal Baru (Target Level: <?php echo htmlspecialchars($target_level); ?>)</h4>
        <p><?php echo htmlspecialchars($new_question); ?></p>
    </div>

    <a href="index.php">Kembali & Coba Lagi</a>
</div>

</body>
</html>