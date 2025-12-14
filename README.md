# Bloomers

Bloomers is a web-based application designed to automatically classify exam or quiz questions into Bloom’s Taxonomy cognitive levels (C1–C6). The application is developed using the Django framework and applies Natural Language Processing (NLP) techniques to support question analysis in educational contexts. This project is intended for academic purposes and focuses on assisting educators and researchers in evaluating cognitive levels of assessment questions.

---

## How It Works

1. Users upload a PDF file containing exam or quiz questions.
2. Text is extracted from the PDF file using PyPDF2.
3. The extracted text undergoes basic NLP preprocessing, including tokenization and text normalization.
4. The system analyzes each question and classifies it into one of Bloom’s cognitive levels (C1–C6).
5. Classification results are displayed through the web interface.

---

## Input

- PDF files containing exam or quiz questions  
- Each sentence or question in the PDF is treated as one individual question  
- Supported languages: Indonesian and English  

---

## Output

- A classification table mapping each question to its corresponding Bloom’s Taxonomy level (C1–C6)
- Visual representation of cognitive level distribution
- Results displayed directly on the web interface

---

## Key Features

- Automatic classification of questions into Bloom’s cognitive levels (C1–C6)
- PDF-based question input
- Text extraction using PyPDF2
- Support for both Indonesian and English questions
- Web-based interface for viewing classification results
- Designed for academic and educational use

---

## Installation Guide

Clone the repository from GitHub to your local machine:

```bash
git clone https://github.com/AgileSoftDev-2025/Automatic-Question-Difficulty-Classification.git

Navigate to the project directory:
cd Automatic-Question-Difficulty-Classification

Create a Python virtual environment:
python -m venv venv

Activate the virtual environment:

-Windows:
venv\Scripts\activate

-Linux/MacOS
source venv/bin/activate

Install required dependencies:
pip install -r requirements.txt

Apply database migrations:
python manage.py migrate

Run the Django development server:
python manage.py runserver

Access the application via a web browser at:
http://127.0.0.1:8000/

---

##Technologies Used

Python

Django

Natural Language Processing (NLP)

PyPDF2

HTML, CSS, JavaScript

SQLite

---

##Notes

Bloomers is developed as an academic project. The classification results depend on the implemented NLP approach and may be further improved through model enhancement and additional feature development.
