<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Regenerate Soal (Rule-Based)</title>
    <style>
        body { 
            font-family: sans-serif; 
            max-width: 600px; 
            margin: 40px auto; 
            background-color: #f4f4f9; 
            color: #333; 
        }

        .container { 
            background-color: #fff; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        header h2 {
            color: #007bff;
            margin: 0;
        }

        .logout-btn {
            padding: 8px 14px;
            background-color: #dc3545;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9rem;
            transition: background-color 0.2s ease;
        }

        .logout-btn:hover {
            background-color: #b52a37;
        }

        textarea, select {
            width: 100%;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
            margin-bottom: 20px;
            font-size: 1rem;
            box-sizing: border-box;
        }

        .levels { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 20px; 
        }

        .level-btn { 
            flex: 1; 
            margin: 0 5px; 
            padding: 10px; 
            border: 1px solid #ccc; 
            background-color: #f9f9f9; 
            cursor: pointer; 
            border-radius: 4px; 
            text-align: center; 
        }

        .level-btn:hover { 
            background-color: #e2e8f0; 
        }

        input[type="submit"] { 
            width: 100%; 
            padding: 12px; 
            background-color: #007bff; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            font-size: 1rem; 
            cursor: pointer; 
        }

        input[type="submit"]:hover { 
            background-color: #0056b3; 
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h2>📝 Regenerate Soal</h2>
        <a href="logout.php" class="logout-btn">Logout</a>
    </header>

    <form action="regenerate.php" method="post">
        <label for="original_question">Masukkan Teks Soal:</label>
        <textarea name="original_question" id="original_question" rows="4" required>Jelaskan secara singkat apa yang dimaksud dengan User Persona dalam proses desain interaksi.</textarea>

        <label for="initial_level">Level Kognitif Awal:</label>
        <select name="initial_level" id="initial_level">
            <option value="C1" selected>C1 (Mengingat)</option>
            <option value="C2">C2 (Memahami)</option>
            <option value="C3">C3 (Menerapkan)</option>
            <option value="C4">C4 (Menganalisis)</option>
            <option value="C5">C5 (Mengevaluasi)</option>
            <option value="C6">C6 (Mencipta)</option>
        </select>

        <label for="target_level">Level Kognitif Target:</label>
        <select name="target_level" id="target_level">
            <option value="C1">C1 (Mengingat)</option>
            <option value="C2">C2 (Memahami)</option>
            <option value="C3">C3 (Menerapkan)</option>
            <option value="C4" selected>C4 (Menganalisis)</option>
            <option value="C5">C5 (Mengevaluasi)</option>
            <option value="C6">C6 (Mencipta)</option>
        </select>
        
        <input type="submit" value="Regenerate Soal">
    </form>
</div>

</body>
</html>
