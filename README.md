# Bloomers

Bloomers is a web-based application developed using the Django framework to automatically classify questions based on their difficulty level and cognitive level. The application applies Natural Language Processing (NLP) techniques to support efficient and consistent analysis of educational questions, helping reduce subjectivity in question evaluation. This system is intended for academic purposes and educational research.

---

## Installation Guide

To run this application locally, follow the steps below.

Clone the repository from GitHub to your local machine:

```bash
git clone https://github.com/AgileSoftDev-2025/Automatic-Question-Difficulty-Classification.git

## Navigate to the project directory:

cd Automatic-Question-Difficulty-Classification

## Create a Python virtual environment:

python -m venv venv

## Activate the virtual environment:

Windows: 

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate


## Install all required dependencies:

pip install -r requirements.txt


## Apply database migrations:

python manage.py migrate


## Run the Django development server:

python manage.py runserver

## Once the server is running, the application can be accessed via a web browser at:

http://127.0.0.1:8000/

---

### Technologies Used

Python

Django

Natural Language Processing (NLP)

HTML, CSS, JavaScript

SQLite

---

Notes

This application is developed for academic purposes and remains open for further enhancement in terms of features and classification accuracy.
