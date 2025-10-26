<?php
// --- DATABASE CONFIGURATION ---
define('DB_SERVER', 'localhost');
define('DB_USERNAME', 'root'); // Default username for XAMPP
define('DB_PASSWORD', '');     // Default password for XAMPP is empty
define('DB_NAME', 'bloomers_db');

// --- ATTEMPT TO CONNECT ---
$conn = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);

// Check the connection
if($conn->connect_error){
    die("FATAL ERROR: Could not connect to the database. " . $conn->connect_error);
}
?>