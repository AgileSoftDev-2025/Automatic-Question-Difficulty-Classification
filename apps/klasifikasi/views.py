from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
from django.conf import settings
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Uncomment when model is ready
# from .models import Classification, Question


@login_required
def hasil_klasifikasi(request, pk=None):
    """
    Display classification results page with better error handling
    """
    try:
        # WHEN MODEL IS READY - Replace dummy data with:
        """
        classification = get_object_or_404(
            Classification,
            pk=pk,
            user=request.user
        )
        
        if classification.status != 'completed':
            messages.warning(request, 'Classification is still processing.')
            return redirect('klasifikasi:history')
        
        questions_data = [
            {
                'question': q.question_text,
                'level': q.category,
                'index': q.question_number,
                'confidence': q.confidence_score
            }
            for q in classification.questions.all()
        ]
        
        filename = classification.filename
        file_url = classification.result_file.url if classification.result_file else '#'
        """
        
        # Dummy data for testing
        questions_data = [
            {
                'question': 'Apa yang dimaksud dengan algoritma dalam pemrograman',
                'level': 'C1',
                'index': 1,
                'confidence': 0.95
            },
            {
                'question': 'Jelaskan perbedaan antara bahasa pemrograman tingkat tinggi dan tingkat rendah',
                'level': 'C2',
                'index': 2,
                'confidence': 0.89
            },
            {
                'question': 'Gunakan struktur percabangan untuk membuat program sederhana menentukan bilangan genap atau ganjil',
                'level': 'C3',
                'index': 3,
                'confidence': 0.92
            },
            {
                'question': 'Analisis penyebab program tidak berjalan dengan benar meskipun sintaks sudah benar',
                'level': 'C4',
                'index': 4,
                'confidence': 0.87
            },
            {
                'question': 'Evaluasi efektivitas penggunaan bubble sort dibandingkan insertion sort untuk dataset besar',
                'level': 'C5',
                'index': 5,
                'confidence': 0.91
            },
            {
                'question': 'Rancang algoritma untuk menghitung total belanja dengan diskon dan pajak menggunakan bahasa pemrograman pilihanmu',
                'level': 'C6',
                'index': 6,
                'confidence': 0.88
            },
            {
                'question': 'Sebutkan tiga jenis topologi jaringan komputer',
                'level': 'C1',
                'index': 7,
                'confidence': 0.94
            },
            {
                'question': 'Jelaskan fungsi dari IP address dalam jaringan komputer',
                'level': 'C2',
                'index': 8,
                'confidence': 0.90
            },
            {
                'question': 'Implementasikan konfigurasi jaringan sederhana menggunakan aplikasi Packet Tracer',
                'level': 'C3',
                'index': 9,
                'confidence': 0.86
            },
            {
                'question': 'Buat rancangan sistem absensi mahasiswa berbasis web dengan mempertimbangkan keamanan data pengguna',
                'level': 'C6',
                'index': 10,
                'confidence': 0.93
            }
        ]
        
        context = {
            'filename': 'Soal Pemrograman dan Jaringan.pdf',
            'file_url': '#',
            'questions': questions_data,
            'labels': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
            'total_questions': len(questions_data),
            'classification_id': pk or 1
        }
        
        return render(request, 'klasifikasi/hasilKlasifikasi.html', context)
        
    except Exception as e:
        logger.error(f"Error in hasil_klasifikasi: {str(e)}")
        messages.error(request, 'An error occurred while loading classification results.')
        return redirect('klasifikasi:history')


@login_required
@csrf_protect
def update_question_classification(request, pk):
    """
    AJAX endpoint to update individual question classification
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        new_category = data.get('category')
        
        if not question_id or not new_category:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Validate category
        valid_categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        if new_category not in valid_categories:
            return JsonResponse({'error': 'Invalid category'}, status=400)
        
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(Classification, pk=pk, user=request.user)
        question = get_object_or_404(Question, id=question_id, classification=classification)
        
        old_category = question.category
        question.category = new_category
        question.save()
        
        # Update classification counts
        setattr(classification, f'q{old_category[1]}_count', 
                getattr(classification, f'q{old_category[1]}_count') - 1)
        setattr(classification, f'q{new_category[1]}_count', 
                getattr(classification, f'q{new_category[1]}_count') + 1)
        classification.save()
        
        logger.info(f"Question {question_id} updated from {old_category} to {new_category}")
        """
        
        return JsonResponse({
            'success': True,
            'message': 'Classification updated successfully',
            'question_id': question_id,
            'new_category': new_category
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error updating question classification: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def home(request):
    """
    Display home page with improved file validation and error handling
    """
    recent_history = []
    
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('klasifikasi:home')
        
        # Enhanced file validation
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            messages.error(
                request, 
                f'File format not supported. Only {", ".join(allowed_extensions)} files are allowed.'
            )
            return redirect('klasifikasi:home')
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            messages.error(
                request, 
                f'File size too large. Maximum file size is 10MB. Your file is {uploaded_file.size / (1024*1024):.1f}MB.'
            )
            return redirect('klasifikasi:home')
        
        # Validate file content (basic check)
        try:
            # Read first few bytes to verify it's not corrupted
            uploaded_file.seek(0)
            header = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            if not header:
                raise ValidationError('File appears to be empty or corrupted')
                
        except Exception as e:
            messages.error(request, f'File validation failed: {str(e)}')
            return redirect('klasifikasi:home')
        
        try:
            # WHEN MODEL IS READY:
            """
            classification = Classification.objects.create(
                user=request.user,
                file=uploaded_file,
                filename=uploaded_file.name,
                file_size=uploaded_file.size,
                status='processing'
            )
            
            # TODO: Queue classification task (using Celery or similar)
            # from .tasks import process_classification
            # process_classification.delay(classification.id)
            
            messages.success(
                request, 
                f'File "{uploaded_file.name}" uploaded successfully and is being processed.'
            )
            return redirect('klasifikasi:hasil_klasifikasi', pk=classification.id)
            """
            
            messages.success(
                request, 
                f'File "{uploaded_file.name}" uploaded successfully. Processing will begin shortly.'
            )
            return redirect('klasifikasi:history')
            
        except Exception as e:
            logger.error(f"Error processing file upload: {str(e)}")
            messages.error(request, f'An error occurred while processing your file: {str(e)}')
            return redirect('klasifikasi:home')
    
    # Get recent history
    try:
        # WHEN MODEL IS READY:
        """
        recent_history = Classification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        """
        pass
    except Exception as e:
        logger.error(f"Error fetching recent history: {str(e)}")
        recent_history = []
    
    context = {
        'recent_history': recent_history,
        'is_authenticated': request.user.is_authenticated,
        'max_file_size_mb': 10,
        'allowed_formats': ['PDF', 'DOC', 'DOCX']
    }
    
    return render(request, 'klasifikasi/home.html', context)


@login_required
def history_view(request):
    """
    Display classification history with enhanced filtering and pagination
    """
    try:
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort', 'date-desc')
        status_filter = request.GET.get('status', 'all')
        
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
        
        # Filter by search
        if search_query:
            classifications_dummy = [
                c for c in classifications_dummy 
                if search_query.lower() in c['filename'].lower()
            ]
        
        # Filter by status
        if status_filter != 'all':
            classifications_dummy = [
                c for c in classifications_dummy 
                if c['status'] == status_filter
            ]
        
        # Apply sorting
        sort_functions = {
            'date-desc': lambda x: datetime.strptime(x['created_at'], '%d/%m/%Y'),
            'date-asc': lambda x: datetime.strptime(x['created_at'], '%d/%m/%Y'),
            'questions-desc': lambda x: x['total_questions'],
            'questions-asc': lambda x: x['total_questions'],
            'name-asc': lambda x: x['filename'].lower(),
            'name-desc': lambda x: x['filename'].lower(),
        }
        
        if sort_by in sort_functions:
            reverse = 'desc' in sort_by
            classifications_dummy.sort(key=sort_functions[sort_by], reverse=reverse)
        
        # Calculate statistics
        total_classifications = len(classifications_dummy)
        total_questions = sum(c['total_questions'] for c in classifications_dummy)
        last_activity = classifications_dummy[0]['created_at'] if classifications_dummy else 'N/A'
        
        # Pagination
        paginator = Paginator(classifications_dummy, 10)
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
            'status_filter': status_filter,
        }
        
        return render(request, 'klasifikasi/history.html', context)
        
    except Exception as e:
        logger.error(f"Error in history_view: {str(e)}")
        messages.error(request, 'An error occurred while loading history.')
        return redirect('klasifikasi:home')


@login_required
@csrf_protect
def delete_classification(request, pk):
    """
    Delete classification with proper error handling
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        # WHEN MODEL IS READY:
        """
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
            except OSError as e:
                logger.warning(f"Could not delete file: {e}")
        
        if classification.result_file and os.path.isfile(classification.result_file.path):
            try:
                os.remove(classification.result_file.path)
            except OSError as e:
                logger.warning(f"Could not delete result file: {e}")
        
        classification.delete()
        
        logger.info(f"Classification {pk} deleted by user {request.user.username}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'"{filename}" deleted successfully'})
        
        messages.success(request, f'Classification "{filename}" deleted successfully.')
        """
        
        # DUMMY response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Classification deleted successfully'})
        
        messages.success(request, 'Classification deleted successfully.')
        return redirect('klasifikasi:history')
        
    except Exception as e:
        logger.error(f"Error deleting classification {pk}: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        
        messages.error(request, f'An error occurred while deleting: {str(e)}')
        return redirect('klasifikasi:history')


@login_required
def view_classification_detail(request, pk):
    """
    Display detailed view of a classification
    """
    try:
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        context = {
            'classification': classification,
        }
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
        
        return render(request, 'klasifikasi/classification_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error viewing classification detail {pk}: {str(e)}")
        messages.error(request, 'An error occurred while loading classification details.')
        return redirect('klasifikasi:history')


@login_required
def download_report(request, pk):
    """
    Download classification report with validation
    """
    try:
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        if not classification.result_file:
            messages.error(request, 'Report file not found.')
            return redirect('klasifikasi:history')
        
        file_path = classification.result_file.path
        
        if not os.path.exists(file_path):
            messages.error(request, 'Report file does not exist.')
            return redirect('klasifikasi:history')
        
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        
        logger.info(f"Report downloaded: {classification.filename} by {request.user.username}")
        
        return response
        """
        
        messages.info(request, 'Report download functionality will be available soon.')
        return redirect('klasifikasi:history')
        
    except Exception as e:
        logger.error(f"Error downloading report {pk}: {str(e)}")
        messages.error(request, f'Error downloading report: {str(e)}')
        return redirect('klasifikasi:history')


@login_required
def view_report(request, pk):
    """
    Display report in web view format
    """
    try:
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        questions = classification.questions.all().order_by('question_number')
        
        context = {
            'classification': classification,
            'questions': questions,
        }
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
            ]
        }
        
        context = {
            'classification': classification_dummy,
        }
        
        return render(request, 'klasifikasi/report_view.html', context)
        
    except Exception as e:
        logger.error(f"Error viewing report {pk}: {str(e)}")
        messages.error(request, 'An error occurred while loading the report.')
        return redirect('klasifikasi:history')


@login_required
def get_classification_stats(request):
    """
    API endpoint for classification statistics (AJAX)
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
        logger.error(f"Error fetching classification stats: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def bulk_delete_classifications(request):
    """
    Delete multiple classifications at once
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
                except Exception as e:
                    logger.warning(f"Could not delete file: {e}")
            
            if classification.result_file and os.path.isfile(classification.result_file.path):
                try:
                    os.remove(classification.result_file.path)
                except Exception as e:
                    logger.warning(f"Could not delete result file: {e}")
            
            classification.delete()
            deleted_count += 1
        
        logger.info(f"Bulk deleted {deleted_count} classifications by user {request.user.username}")
        
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
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)