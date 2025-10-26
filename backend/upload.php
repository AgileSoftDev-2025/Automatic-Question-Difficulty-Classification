<?php
session_start(); // Cek user login

if (!isset($_FILES['file'])) {
    echo json_encode(["success" => false, "message" => "Tidak ada file yang diupload."]);
    exit;
}

$file = $_FILES['file'];
$tempPath = $file['tmp_name'];
$fileName = basename($file['name']);
$targetDir = __DIR__ . "/backend/uploads/";
$targetPath = $targetDir . $fileName;<?php
session_start();

header('Content-Type: application/json');

if (!isset($_FILES['file'])) {
    echo json_encode(["success" => false, "message" => "Tidak ada file yang diunggah."]);
    exit;
}

$file = $_FILES['file'];
$tempPath = $file['tmp_name'];
$fileName = basename($file['name']);
$fileSize = $file['size'];
$fileType = $file['type'];

$targetDir = __DIR__ . "/backend/uploads/";
$targetPath = $targetDir . $fileName;

$allowedTypes = [
    'text/csv',
    'application/pdf',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];
$maxSize = 5 * 1024 * 1024;

if (!in_array($fileType, $allowedTypes)) {
    echo json_encode(["success" => false, "message" => "Format file tidak didukung."]);
    exit;
}

if ($fileSize > $maxSize) {
    echo json_encode(["success" => false, "message" => "Ukuran file melebihi 5 MB."]);
    exit;
}

// Cek dah login atau belum?
if (isset($_SESSION['user_id'])) {
    $userId = $_SESSION['user_id'];

    if (!file_exists($targetDir)) {
        mkdir($targetDir, 0777, true);
    }

    // Simpan file ke database
    if (move_uploaded_file($tempPath, $targetPath)) {
        require_once 'db_connect.php';

        $stmt = $conn->prepare("INSERT INTO file_uploads (user_id, file_name, file_type, file_size, upload_time) VALUES (?, ?, ?, ?, NOW())");
        $stmt->bind_param("issi", $userId, $fileName, $fileType, $fileSize);
        $stmt->execute();

        echo json_encode([
            "success" => true,
            "message" => "File berhasil diunggah dan disimpan di database.",
            "file" => $fileName
        ]);
    } else {
        echo json_encode(["success" => false, "message" => "Gagal menyimpan file."]);
    }

} else {
    // Belom Login
    $result = [
        "status" => "processed",
        "filename" => $fileName,
        "classification" => "Kategori A (simulasi)"
    ];

    echo json_encode([
        "success" => true,
        "message" => "File berhasil diunggah sementara (tidak disimpan karena belum login).",
        "result" => $result
    ]);
}
?>


// Cek login
if (isset($_SESSION['user_id'])) {
    if (!file_exists($targetDir)) {
        mkdir($targetDir, 0777, true);
    }

    if (move_uploaded_file($tempPath, $targetPath)) {
        require_once 'db_connect.php';
        $userId = $_SESSION['user_id'];

        $stmt = $conn->prepare("INSERT INTO file_uploads (user_id, file_name, upload_time) VALUES (?, ?, NOW())");
        $stmt->bind_param("is", $userId, $fileName);
        $stmt->execute();

        echo json_encode(["success" => true, "message" => "File berhasil diupload dan disimpan ke database."]);
    } else {
        echo json_encode(["success" => false, "message" => "Gagal menyimpan file."]);
    }
} else { // Tidak login
    echo json_encode([
        "success" => true,
        "message" => "File diproses sementara."
    ]);
}
?>
