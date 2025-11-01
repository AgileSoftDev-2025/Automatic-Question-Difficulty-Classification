# apps/soal/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
import os
from django.core.cache import cache
import uuid

from .models import ClassificationHistory

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def home(request):
    context = {'is_authenticated': request.user.is_authenticated}
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        if not allowed_file(uploaded_file.name):
            # Ini akan memicu pop-up error
            messages.error(request, 'Invalid file type. Please upload PDF, CSV, TXT, or DOCX files only.')
            # Muat ulang halaman, pop-up akan muncul
            return redirect('soal:home') # Asumsi URL 'home' Anda

        try:
            if request.user.is_authenticated:
                # Save file permanently for logged in users
                fs = FileSystemStorage(location='media/uploads/')
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(filename)
                
                ClassificationHistory.objects.create(
                    user=request.user,
                    filename=filename,
                    file_url=file_url
                )
            else:
                # Store in cache for non-logged in users
                cache_key = f'temp_file_{uuid.uuid4()}'
                cache.set(cache_key, uploaded_file.read(), timeout=3600) 
                context['cache_key'] = cache_key
            
            # Ini akan memicu pop-up sukses
            messages.success(request, 'File uploaded successfully!')
            
        except Exception as e:
            # Ini akan memicu pop-up error
            messages.error(request, f'Error uploading file: {str(e)}')
        
        # Selalu redirect setelah POST sukses untuk menghindari submit ulang
        return redirect('soal:home') # Asumsi URL 'home' Anda
            
    if request.user.is_authenticated:
        # Get user's classification history
        context['history'] = ClassificationHistory.objects.filter(user=request.user).order_by('-created_at')
        
    return render(request, 'soal/home.html', context)