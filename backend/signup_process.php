<?php
require_once "db.php"; // Include the database connection

$username = trim($_POST["username"]);
$email = trim($_POST["email"]);
$password = trim($_POST["password"]);

$errors = [];

// --- VALIDATION ---
// Username validation
if (empty($username)) {
    $errors[] = "Username is required.";
} else {
    $sql = "SELECT id FROM users WHERE username = ?";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $stmt->store_result();
        if ($stmt->num_rows > 0) {
            $errors[] = "This username is already taken.";
        }
        $stmt->close();
    }
}

// Email validation
if (empty($email)) {
    $errors[] = "Email is required.";
} else if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = "Invalid email format.";
} else {
    $sql = "SELECT id FROM users WHERE email = ?";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $stmt->store_result();
        if ($stmt->num_rows > 0) {
            $errors[] = "This email is already registered.";
        }
        $stmt->close();
    }
}

// Password validation
if (empty($password) || strlen($password) < 6) {
    $errors[] = "Password must be at least 6 characters long.";
}

// --- INSERT INTO DATABASE ---
if (empty($errors)) {
    // Hash the password for security
    $hashed_password = password_hash($password, PASSWORD_DEFAULT);
    
    $sql = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param("sss", $username, $email, $hashed_password);
        if ($stmt->execute()) {
            // Redirect to login page on success
            header("location: login.html");
            exit();
        } else {
            $errors[] = "Something went wrong. Please try again later.";
        }
        $stmt->close();
    }
}

// --- DISPLAY ERRORS ---
if (!empty($errors)) {
    echo "<h2>Error Signing Up</h2>";
    foreach($errors as $error) {
        echo "<p>" . htmlspecialchars($error) . "</p>";
    }
    echo "<a href='signup.html'>Go back to Signup</a>";
}

$conn->close();
?>