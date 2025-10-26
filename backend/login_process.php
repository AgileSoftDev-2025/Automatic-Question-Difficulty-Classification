<?php
// Mulai session
session_start();
 
// Jika pengguna sudah login, arahkan ke halaman utama (index.php)
if(isset($_SESSION["loggedin"]) && $_SESSION["loggedin"] === true){
    header("location: index.php"); // <-- PERUBAHAN DI SINI
    exit;
}
 
require_once "db.php"; // Sertakan koneksi database
 
$username_email = trim($_POST["username"]);
$password = trim($_POST["password"]);
$login_err = "";

// Validasi kredensial
if(empty($username_email) || empty($password)){
    $login_err = "Silakan masukkan username/email dan password.";
} else {
    // Cari pengguna berdasarkan username ATAU email
    $sql = "SELECT id, username, password FROM users WHERE username = ? OR email = ?";
    
    if($stmt = $conn->prepare($sql)){
        // Bind variabel ke prepared statement sebagai parameter
        $stmt->bind_param("ss", $username_email, $username_email);
        
        if($stmt->execute()){
            $stmt->store_result();
            
            if($stmt->num_rows == 1){
                $stmt->bind_result($id, $username, $hashed_password);
                if($stmt->fetch()){
                    // Verifikasi password
                    if(password_verify($password, $hashed_password)){
                        // Password benar, mulai session baru
                        session_start();
                        
                        // Simpan data di variabel session
                        $_SESSION["loggedin"] = true;
                        $_SESSION["id"] = $id;
                        $_SESSION["username"] = $username;
                        
                        // Arahkan pengguna ke halaman index.php setelah login berhasil
                        header("location: index.php"); // <-- PERUBAHAN DI SINI
                    } else {
                        $login_err = "Username/email atau password salah.";
                    }
                }
            } else {
                $login_err = "Username/email atau password salah.";
            }
        } else {
            $login_err = "Oops! Terjadi kesalahan. Silakan coba lagi nanti.";
        }
        $stmt->close();
    }
}
 
$conn->close();

// --- TAMPILKAN ERROR JIKA ADA ---
if (!empty($login_err)) {
    echo "<h2>Login Gagal</h2>";
    echo "<p>" . htmlspecialchars($login_err) . "</p>";
    echo "<a href='login.html'>Kembali ke Halaman Login</a>";
}
?>