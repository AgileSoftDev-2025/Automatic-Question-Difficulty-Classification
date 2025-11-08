# ===================================
# FILE: views.py (untuk app klasifikasi)
# ===================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
import os
from django.conf import settings
import json
from datetime import datetime

# Uncomment when model is ready
# from .models import Classification


@login_required
def home(request):
    """
    Menampilkan halaman utama (homepage) dengan form upload
    """
    recent_history = []
    
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            messages.error(request, 'Tidak ada file yang dipilih.')
            return redirect('klasifikasi:home')
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            messages.error(request, f'Format file tidak didukung. Hanya {", ".join(allowed_extensions)} yang diperbolehkan.')
            return redirect('klasifikasi:home')
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            messages.error(request, 'Ukuran file terlalu besar. Maksimal 10MB.')
            return redirect('klasifikasi:home')
        
        try:
            # TODO: Process the file and create classification
            # classification = Classification.objects.create(
            #     user=request.user,
            #     file=uploaded_file,
            #     filename=uploaded_file.name,
            #     status='processing'
            # )
            
            # TODO: Call your ML model to classify questions
            # process_classification(classification.id)
            
            messages.success(request, f'File "{uploaded_file.name}" berhasil diupload dan sedang diproses.')
            return redirect('klasifikasi:history')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat memproses file: {str(e)}')
            return redirect('klasifikasi:home')
    
    # Get recent history (5 most recent)
    try:
        # Uncomment when model is ready
        # recent_history = Classification.objects.filter(
        #     user=request.user
        # ).order_by('-created_at')[:5]
        pass
    except Exception as e:
        print(f"Error fetching recent history: {e}")
        recent_history = []
    
    context = {
        'recent_history': recent_history,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'klasifikasi/home.html', context)


@login_required
def history_view(request):
    """
    Menampilkan halaman history klasifikasi dengan pagination, search, dan filter
    """
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Get sort parameter
    sort_by = request.GET.get('sort', 'date-desc')
    
    # DUMMY DATA - Replace with actual model query
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
        {
            'id': 3,
            'filename': 'Quiz Matematika.pdf',
            'total_questions': 15,
            'created_at': '22/3/2024',
            'q1_count': 3,
            'q2_count': 4,
            'q3_count': 2,
            'q4_count': 4,
            'q5_count': 2,
            'q6_count': 0,
            'status': 'completed',
        },
    ]
    
    # Calculate statistics
    total_classifications = len(classifications_dummy)
    total_questions = sum(c['total_questions'] for c in classifications_dummy)
    last_activity = classifications_dummy[0]['created_at'] if classifications_dummy else 'N/A'
    
    # Filter by search query
    if search_query:
        classifications_dummy = [
            c for c in classifications_dummy 
            if search_query.lower() in c['filename'].lower()
        ]
    
    # Apply sorting
    if sort_by == 'date-desc':
        classifications_dummy.sort(key=lambda x: datetime.strptime(x['created_at'], '%d/%m/%Y'), reverse=True)
    elif sort_by == 'date-asc':
        classifications_dummy.sort(key=lambda x: datetime.strptime(x['created_at'], '%d/%m/%Y'))
    elif sort_by == 'questions-desc':
        classifications_dummy.sort(key=lambda x: x['total_questions'], reverse=True)
    elif sort_by == 'questions-asc':
        classifications_dummy.sort(key=lambda x: x['total_questions'])
    
    # Pagination
    paginator = Paginator(classifications_dummy, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)
    
    context = {
        'classifications': page_obj,
        'total_classifications': total_classifications,
        'total_questions': total_questions,
        'last_activity': last_activity,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    # WHEN MODEL IS READY, use this code:
    """
    from .models import Classification
    
    # Base queryset
    classifications = Classification.objects.filter(user=request.user)
    
    # Apply search filter
    if search_query:
        classifications = classifications.filter(
            Q(filename__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'date-desc':
        classifications = classifications.order_by('-created_at')
    elif sort_by == 'date-asc':
        classifications = classifications.order_by('created_at')
    elif sort_by == 'questions-desc':
        classifications = classifications.order_by('-total_questions')
    elif sort_by == 'questions-asc':
        classifications = classifications.order_by('total_questions')
    else:
        classifications = classifications.order_by('-created_at')
    
    # Calculate statistics
    stats = classifications.aggregate(
        total_questions=Sum('total_questions'),
    )
    
    total_classifications = classifications.count()
    total_questions = stats['total_questions'] or 0
    
    # Get last activity
    last_classification = classifications.first()
    last_activity = last_classification.created_at.strftime('%d/%m/%Y') if last_classification else 'N/A'
    
    # Pagination
    paginator = Paginator(classifications, 10)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)
    
    context = {
        'classifications': page_obj,
        'total_classifications': total_classifications,
        'total_questions': total_questions,
        'last_activity': last_activity,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    """
    
    return render(request, 'klasifikasi/history.html', context)


@login_required
@csrf_protect
def delete_classification(request, pk):
    """
    Menghapus klasifikasi berdasarkan ID
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('klasifikasi:history')
    
    # DUMMY implementation
    messages.success(request, 'Classification deleted successfully.')
    return redirect('klasifikasi:history')
    
    # WHEN MODEL IS READY, use this code:
    """
    from .models import Classification
    
    try:
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        filename = classification.filename
        
        # Delete associated files
        if classification.file and os.path.isfile(classification.file.path):
            try:
                os.remove(classification.file.path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        if hasattr(classification, 'result_file') and classification.result_file:
            if os.path.isfile(classification.result_file.path):
                try:
                    os.remove(classification.result_file.path)
                except Exception as e:
                    print(f"Error deleting result file: {e}")
        
        # Delete the classification record
        classification.delete()
        
        messages.success(request, f'Classification "{filename}" has been deleted successfully.')
        
    except Classification.DoesNotExist:
        messages.error(request, 'Classification not found.')
    except Exception as e:
        messages.error(request, f'An error occurred while deleting: {str(e)}')
    
    return redirect('klasifikasi:history')
    """


@login_required
def view_classification_detail(request, pk):
    """
    Menampilkan detail klasifikasi
    """
    # DUMMY implementation
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
        'status': 'completed',
        'processed_at': '15/2/2024 10:30',
        'file_size': '2.5 MB',
    }
    
    context = {
        'classification': classification_dummy,
    }
    
    # WHEN MODEL IS READY:
    """
    from .models import Classification
    
    try:
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        context = {
            'classification': classification,
        }
        
    except Classification.DoesNotExist:
        messages.error(request, 'Classification not found.')
        return redirect('klasifikasi:history')
    """
    
    return render(request, 'klasifikasi/classification_detail.html', context)


@login_required
def download_report(request, pk):
    """
    Download laporan klasifikasi dalam format file
    """
    # WHEN MODEL IS READY:
    """
    from .models import Classification
    
    try:
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        if not hasattr(classification, 'result_file') or not classification.result_file:
            messages.error(request, 'Report file not found.')
            return redirect('klasifikasi:history')
        
        file_path = classification.result_file.path
        
        if not os.path.exists(file_path):
            messages.error(request, 'Report file does not exist on server.')
            return redirect('klasifikasi:history')
        
        # Open and return file
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
        
    except Classification.DoesNotExist:
        messages.error(request, 'Classification not found.')
        return redirect('klasifikasi:history')
    except Exception as e:
        messages.error(request, f'Error downloading report: {str(e)}')
        return redirect('klasifikasi:history')
    """
    
    # DUMMY implementation
    messages.error(request, 'Report download not yet implemented.')
    return redirect('klasifikasi:history')


@login_required
def view_report(request, pk):
    """
    Menampilkan report dalam bentuk preview/web view
    """
    # DUMMY implementation
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
        'questions': [
            {
                'number': 1,
                'text': 'What is the capital of France?',
                'category': 'C1',
                'category_name': 'Remember',
            },
            {
                'number': 2,
                'text': 'Explain the water cycle.',
                'category': 'C2',
                'category_name': 'Understand',
            },
            # Add more dummy questions as needed
        ]
    }
    
    context = {
        'classification': classification_dummy,
    }
    
    # WHEN MODEL IS READY:
    """
    from .models import Classification
    
    try:
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        # Get all questions for this classification
        questions = classification.questions.all().order_by('question_number')
        
        context = {
            'classification': classification,
            'questions': questions,
        }
        
    except Classification.DoesNotExist:
        messages.error(request, 'Classification not found.')
        return redirect('klasifikasi:history')
    """
    
    return render(request, 'klasifikasi/report_view.html', context)


@login_required
def get_classification_stats(request):
    """
    API endpoint untuk mendapatkan statistik klasifikasi (untuk AJAX calls)
    """
    try:
        # DUMMY data
        stats = {
            'total_classifications': 3,
            'total_questions': 48,
            'categories': {
                'C1': 10,
                'C2': 13,
                'C3': 6,
                'C4': 12,
                'C5': 5,
                'C6': 2,
            },
            'recent_activity': [
                {
                    'id': 1,
                    'filename': 'Soal UTS.pdf',
                    'date': '15/2/2024',
                    'questions': 10
                }
            ]
        }
        
        # WHEN MODEL IS READY:
        """
        from .models import Classification
        from django.db.models import Count, Sum
        
        classifications = Classification.objects.filter(user=request.user)
        
        stats = {
            'total_classifications': classifications.count(),
            'total_questions': classifications.aggregate(Sum('total_questions'))['total_questions__sum'] or 0,
            'categories': {
                'C1': classifications.aggregate(Sum('q1_count'))['q1_count__sum'] or 0,
                'C2': classifications.aggregate(Sum('q2_count'))['q2_count__sum'] or 0,
                'C3': classifications.aggregate(Sum('q3_count'))['q3_count__sum'] or 0,
                'C4': classifications.aggregate(Sum('q4_count'))['q4_count__sum'] or 0,
                'C5': classifications.aggregate(Sum('q5_count'))['q5_count__sum'] or 0,
                'C6': classifications.aggregate(Sum('q6_count'))['q6_count__sum'] or 0,
            },
            'recent_activity': [
                {
                    'id': c.id,
                    'filename': c.filename,
                    'date': c.created_at.strftime('%d/%m/%Y'),
                    'questions': c.total_questions
                }
                for c in classifications.order_by('-created_at')[:5]
            ]
        }
        """
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def bulk_delete_classifications(request):
    """
    Menghapus multiple classifications sekaligus
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'error': 'No IDs provided'}, status=400)
        
        # WHEN MODEL IS READY:
        """
        from .models import Classification
        
        classifications = Classification.objects.filter(
            pk__in=ids,
            user=request.user
        )
        
        deleted_count = 0
        for classification in classifications:
            # Delete files
            if classification.file and os.path.isfile(classification.file.path):
                try:
                    os.remove(classification.file.path)
                except:
                    pass
            
            if hasattr(classification, 'result_file') and classification.result_file:
                if os.path.isfile(classification.result_file.path):
                    try:
                        os.remove(classification.result_file.path)
                    except:
                        pass
            
            classification.delete()
            deleted_count += 1
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'{deleted_count} classification(s) deleted successfully'
        })
        """
        
        # DUMMY response
        return JsonResponse({
            'success': True,
            'deleted_count': len(ids),
            'message': f'{len(ids)} classification(s) deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)