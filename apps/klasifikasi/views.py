# ===================================
# FILE: views.py (untuk app klasifikasi)
# ===================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
# from .models import Classification  # Uncomment jika model sudah dibuat
import os
from django.conf import settings

@login_required
def home(request):
    """
    Menampilkan halaman utama (homepage)
    """
    history = [] # Ganti dengan data asli jika perlu
    
    # Logika untuk form upload file Anda akan ada di sini
    if request.method == 'POST':
        # Contoh: proses file upload
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # Lakukan sesuatu dengan file (simpan, proses, dll.)
            messages.success(request, f'File "{uploaded_file.name}" berhasil diupload.')
            # Arahkan ke halaman hasil atau history
            return redirect('klasifikasi:history') 
        else:
            messages.error(request, 'Tidak ada file yang dipilih.')

    # Ambil 5 history terbaru untuk ditampilkan di homepage
    # Ganti 'classifications_dummy' dengan query model asli nanti
    try:
        # GANTI DENGAN MODEL ASLI
        # history = Classification.objects.filter(user=request.user).order_by('-created_at')[:5]
        pass # Hapus 'pass' ini saat model sudah ada
    except Exception as e:
        history = [] # Tetap kosong jika ada error

    context = {
        'history': history,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'klasifikasi/home.html', context)

@login_required
def history_view(request):
    """
    Menampilkan halaman history klasifikasi untuk user yang sedang login
    """
    # SEMENTARA: Data dummy untuk testing
    # Hapus bagian ini setelah model dibuat
    classifications_dummy = [
        {
            'id': 1,
            'filename': 'Soal UTS.pdf',
            'total_questions': 10,
            'created_at': '15/2/2024',
            'q1_count': 2,
            'q2_count': 2,
            'q3_count': 1,
            'q4_count': 3,
            'q5_count': 2,
            'q6_count': 0,
            'status': 'completed',
        },
        {
            'id': 2,
            'filename': 'Soal apa aja.pdf',
            'total_questions': 23,
            'created_at': '19/3/2024',
            'q1_count': 5,
            'q2_count': 7,
            'q3_count': 3,
            'q4_count': 5,
            'q5_count': 1,
            'q6_count': 2,
            'status': 'completed',
        },
    ]
    
    context = {
        'classifications': classifications_dummy,
        'total_classifications': len(classifications_dummy),
    }
    
    # SETELAH MODEL DIBUAT, uncomment kode ini dan hapus dummy data di atas:
    """
    from .models import Classification
    
    classifications = Classification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    paginator = Paginator(classifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'classifications': page_obj,
        'total_classifications': classifications.count(),
    }
    """
    
    return render(request, 'klasifikasi/history.html', context)


@login_required
@csrf_protect
def delete_classification(request, pk):
    """
    Menghapus klasifikasi berdasarkan ID
    """
    # SETELAH MODEL DIBUAT, uncomment kode ini:
    """
    from .models import Classification
    
    classification = get_object_or_404(Classification, pk=pk, user=request.user)
    
    if request.method == 'POST':
        if classification.file:
            if os.path.isfile(classification.file.path):
                os.remove(classification.file.path)
        
        if classification.result_file:
            if os.path.isfile(classification.result_file.path):
                os.remove(classification.result_file.path)
        
        filename = classification.filename
        classification.delete()
        messages.success(request, f'Classification "{filename}" has been deleted successfully.')
    """
    
    # DUMMY untuk sementara
    messages.success(request, 'Classification deleted successfully.')
    return redirect('klasifikasi:history')


@login_required
def view_classification_detail(request, pk):
    """
    Menampilkan detail klasifikasi
    """
    # DUMMY untuk sementara
    classification_dummy = {
        'id': pk,
        'filename': 'Soal UTS.pdf',
        'total_questions': 10,
        'created_at': '15/2/2024',
        'q1_count': 2,
        'q2_count': 2,
        'q3_count': 1,
        'q4_count': 3,
        'q5_count': 2,
        'q6_count': 0,
    }
    
    context = {
        'classification': classification_dummy,
    }
    
    # SETELAH MODEL DIBUAT, uncomment:
    """
    from .models import Classification
    classification = get_object_or_404(Classification, pk=pk, user=request.user)
    context = {'classification': classification}
    """
    
    return render(request, 'klasifikasi/classification_detail.html', context)


@login_required
def download_report(request, pk):
    """
    Download laporan klasifikasi dalam format file
    """
    # SETELAH MODEL DIBUAT, uncomment:
    """
    from .models import Classification
    
    classification = get_object_or_404(Classification, pk=pk, user=request.user)
    
    if classification.result_file:
        file_path = classification.result_file.path
        
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    """
    
    messages.error(request, 'Report file not found.')
    return redirect('klasifikasi:history')


@login_required
def view_report(request, pk):
    """
    Menampilkan report dalam bentuk preview
    """
    # DUMMY untuk sementara
    classification_dummy = {
        'id': pk,
        'filename': 'Soal UTS.pdf',
        'total_questions': 10,
        'q1_count': 2,
        'q2_count': 2,
        'q3_count': 1,
        'q4_count': 3,
        'q5_count': 2,
        'q6_count': 0,
    }
    
    context = {
        'classification': classification_dummy,
    }
    
    return render(request, 'klasifikasi/report_view.html', context)