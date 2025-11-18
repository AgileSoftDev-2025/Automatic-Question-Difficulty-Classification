import os
import sys
import django

def before_all(context):
    # Path to directory (Isi sesuai direktori kalian)
    project_path = r"D:\1. Rehan\0. KULIAH\2. MATA KULIAH\SEMESTER 5\11. Pembangunan Perangkat Lunak Praktikum"

    # Add project path to sys.path
    sys.path.insert(0, project_path)