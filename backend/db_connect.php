<?php
// Konfigurasi database sementara
$host = "localhost";       // Ganti sesuai environment
$user = "root";            // Ganti sesuai username database
$pass = "";                // Ganti sesuai password database
$dbname = "bloomers_db";   // Database (nama)

$conn = new mysqli($host, $user, $pass, $dbname);

// Cek koneksi
if ($conn->connect_error) {
    die("Koneksi gagal: " . $conn->connect_error);
}
?>

$host = "localhost";       // Sesuaikan environment
$user = "root";            // Ganti sesuai username database kamu
$pass = "";                // Ganti sesuai password database kamu
$dbname = "bloomers_db";   // Nama database

$conn = new mysqli($host, $user, $pass, $dbname);

// Cek koneksi
if ($conn->connect_error) {
    die("Koneksi gagal: " . $conn->connect_error);
}
?>
