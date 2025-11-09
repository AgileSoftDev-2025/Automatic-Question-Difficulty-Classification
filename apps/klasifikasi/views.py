"""
Improved views for Classification System
Enhanced error handling, security, and functionality
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import os
import json
from datetime import datetime, timedelta
import logging
import mimetypes

logger = logging.getLogger(__name__)

# Uncomment when models are ready
# from .models import Classification, Question


@login_required
@require_http_methods(["GET"])
def hasil_klasifikasi(request, pk=None):
    """
    Display classification results page with enhanced features
    """
    try:
        # WHEN MODEL IS READY - Replace dummy data with:
        """
        classification = get_object_or_404(
            Classification,
            pk=pk,
            user=request.user
        )
        
        # Check if classification is completed
        if classification.status != 'completed':
            messages.warning(
                request, 
                f'Classification is still {classification.status}. Please wait.'
            )
            return redirect('klasifikasi:history')
        
        # Get all questions ordered by number
        questions = classification.questions.select_related('classification').order_by('question_number')
        
        questions_data = [
            {
                'question': q.question_text,
                'level': q.category,
                'index': q.question_number,
                'confidence': q.confidence_score * 100,  # Convert to percentage
                'choices': q.has_choices,
                'is_manually_classified': q.is_manually_classified
            }
            for q in questions
        ]
        
        filename = classification.filename
        file_url = classification.result_file.url if classification.result_file else '#'
        classification_date = classification.formatted_created_at
        total_questions = classification.total_questions
        """
        
        # DUMMY DATA for testing
        questions_data = [
            {
                'question': 'Apa yang dimaksud dengan algoritma dalam pemrograman?',
                'level': 'C1',
                'index': 1,
                'confidence': 95
            },
            {
                'question': 'Jelaskan perbedaan antara bahasa pemrograman tingkat tinggi dan tingkat rendah',
                'level': 'C2',
                'index': 2,
                'confidence': 89
            },
            {
                'question': 'Gunakan struktur percabangan untuk membuat program sederhana menentukan bilangan genap atau ganjil',
                'level': 'C3',
                'index': 3,
                'confidence': 92
            },
            {
                'question': 'Analisis penyebab program tidak berjalan dengan benar meskipun sintaks sudah benar',
                'level': 'C4',
                'index': 4,
                'confidence': 87
            },
            {
                'question': 'Evaluasi efektivitas penggunaan bubble sort dibandingkan insertion sort untuk dataset besar',
                'level': 'C5',
                'index': 5,
                'confidence': 91
            },
            {
                'question': 'Rancang algoritma untuk menghitung total belanja dengan diskon dan pajak menggunakan bahasa pemrograman pilihanmu',
                'level': 'C6',
                'index': 6,
                'confidence': 88
            },
            {
                'question': 'Sebutkan tiga jenis topologi jaringan komputer',
                'level': 'C1',
                'index': 7,
                'confidence': 94
            },
            {
                'question': 'Jelaskan fungsi dari IP address dalam jaringan komputer',
                'level': 'C2',
                'index': 8,
                'confidence': 90
            },
            {
                'question': 'Implementasikan konfigurasi jaringan sederhana menggunakan aplikasi Packet Tracer',
                'level': 'C3',
                'index': 9,
                'confidence': 86
            },
            {
                'question': 'Buat rancangan sistem absensi mahasiswa berbasis web dengan mempertimbangkan keamanan data pengguna',
                'level': 'C6',
                'index': 10,
                'confidence': 93
            },
            {
                'question': 'Apa itu variabel dalam pemrograman?',
                'level': 'C1',
                'index': 11,
                'confidence': 96
            },
            {
                'question': 'Jelaskan konsep loop dalam pemrograman',
                'level': 'C2',
                'index': 12,
                'confidence': 88
            },
            {
                'question': 'Terapkan konsep array untuk menyimpan data mahasiswa',
                'level': 'C3',
                'index': 13,
                'confidence': 85
            },
            {
                'question': 'Bandingkan efisiensi algoritma sorting berbeda',
                'level': 'C4',
                'index': 14,
                'confidence': 90
            },
            {
                'question': 'Evaluasi keamanan sistem login yang ada',
                'level': 'C5',
                'index': 15,
                'confidence': 87
            },
            {
                'question': 'Desain database untuk sistem perpustakaan',
                'level': 'C6',
                'index': 16,
                'confidence': 89
            },
            {
                'question': 'Sebutkan jenis-jenis operator dalam pemrograman',
                'level': 'C1',
                'index': 17,
                'confidence': 95
            },
            {
                'question': 'Jelaskan perbedaan GET dan POST method',
                'level': 'C2',
                'index': 18,
                'confidence': 91
            },
            {
                'question': 'Implementasikan CRUD operations untuk data siswa',
                'level': 'C3',
                'index': 19,
                'confidence': 88
            },
            {
                'question': 'Analisis performa aplikasi web Anda',
                'level': 'C4',
                'index': 20,
                'confidence': 86
            },
            {
                'question': 'Rancang arsitektur microservices untuk e-commerce',
                'level': 'C6',
                'index': 21,
                'confidence': 92
            },
        ]
        
        filename = 'SOAL LATIHAN UTS.pdf'
        file_url = '#'
        classification_date = timezone.now().strftime('%d/%m/%Y')
        total_questions = len(questions_data)
        
        context = {
            'filename': filename,
            'file_url': file_url,
            'questions': questions_data,
            'labels': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
            'total_questions': total_questions,
            'classification_id': pk or 1,
            'classification_date': classification_date,
        }
        
        return render(request, 'klasifikasi/hasilKlasifikasi.html', context)
        
    except Exception as e:
        logger.error(f"Error in hasil_klasifikasi view: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading classification results.')
        return redirect('klasifikasi:history')


@login_required
@csrf_protect
@require_POST
def update_question_classification(request, pk):
    """
    AJAX endpoint to update individual question classification
    Enhanced with better validation and error handling
    """
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        question_id = data.get('question_id')
        new_category = data.get('category')
        
        # Validate required fields
        if not question_id or not new_category:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: question_id and category'
            }, status=400)
        
        # Validate category
        valid_categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        if new_category not in valid_categories:
            return JsonResponse({
                'success': False,
                'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            }, status=400)
        
        # WHEN MODEL IS READY:
        """
        # Get classification and verify ownership
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        # Get question and verify it belongs to this classification
        question = get_object_or_404(
            Question, 
            id=question_id, 
            classification=classification
        )
        
        # Store old category for logging
        old_category = question.category
        
        # Update question category
        question.category = new_category
        question.save()
        
        # Recalculate classification counts
        classification.recalculate_counts()
        
        logger.info(
            f"Question {question_id} updated from {old_category} to {new_category} "
            f"by user {request.user.username} in classification {pk}"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Classification updated successfully',
            'question_id': question_id,
            'old_category': old_category,
            'new_category': new_category,
            'updated_counts': {
                'C1': classification.q1_count,
                'C2': classification.q2_count,
                'C3': classification.q3_count,
                'C4': classification.q4_count,
                'C5': classification.q5_count,
                'C6': classification.q6_count,
            }
        })
        """
        
        # DUMMY response for testing
        logger.info(
            f"Question {question_id} would be updated to {new_category} "
            f"by user {request.user.username} in classification {pk}"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Classification updated successfully',
            'question_id': question_id,
            'new_category': new_category
        })
        
    except Exception as e:
        logger.error(f"Error updating question classification: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An internal error occurred while updating classification'
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
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
            size_mb = uploaded_file.size / (1024 * 1024)
            messages.error(
                request, 
                f'File size too large. Maximum file size is 10MB. Your file is {size_mb:.1f}MB.'
            )
            return redirect('klasifikasi:home')
        
        # Validate file content (basic check)
        try:
            uploaded_file.seek(0)
            header = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            if not header:
                raise ValidationError('File appears to be empty')
            
            # Validate MIME type
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            allowed_mimes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            
            if mime_type not in allowed_mimes:
                raise ValidationError('Invalid file type detected')
                
        except Exception as e:
            logger.warning(f"File validation failed: {str(e)}")
            messages.error(request, f'File validation failed: {str(e)}')
            return redirect('klasifikasi:home')
        
        try:
            # WHEN MODEL IS READY:
            """
            # Check for duplicate files (by hash)
            file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()
            uploaded_file.seek(0)
            
            duplicate = Classification.objects.filter(
                user=request.user,
                file_hash=file_hash
            ).first()
            
            if duplicate:
                messages.warning(
                    request,
                    f'This file has already been uploaded on {duplicate.formatted_created_at}.'
                )
                return redirect('klasifikasi:hasil_klasifikasi', pk=duplicate.id)
            
            classification = Classification.objects.create(
                user=request.user,
                file=uploaded_file,
                filename=uploaded_file.name,
                file_size=uploaded_file.size,
                file_hash=file_hash,
                status='pending'
            )
            
            # TODO: Queue classification task (using Celery)
            # from .tasks import process_classification
            # task = process_classification.delay(classification.id)
            # classification.task_id = task.id
            # classification.save()
            
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
            logger.error(f"Error processing file upload: {str(e)}", exc_info=True)
            messages.error(request, f'An error occurred while processing your file.')
            return redirect('klasifikasi:home')
    
    # GET request - show home page
    try:
        # WHEN MODEL IS READY:
        """
        recent_history = Classification.objects.filter(
            user=request.user
        ).select_related('user').order_by('-created_at')[:5]
        
        # Get statistics
        stats = Classification.objects.filter(
            user=request.user,
            status='completed'
        ).aggregate(
            total=Count('id'),
            total_questions=Sum('total_questions'),
            avg_processing_time=Avg('processing_time_seconds')
        )
        """
        stats = {
            'total': 0,
            'total_questions': 0,
            'avg_processing_time': 0
        }
    except Exception as e:
        logger.error(f"Error fetching recent history: {str(e)}", exc_info=True)
        recent_history = []
        stats = {}
    
    context = {
        'recent_history': recent_history,
        'stats': stats,
        'is_authenticated': request.user.is_authenticated,
        'max_file_size_mb': 10,
        'allowed_formats': ['PDF', 'DOC', 'DOCX']
    }
    
    return render(request, 'klasifikasi/home.html', context)


@login_required
@require_http_methods(["GET"])
def history_view(request):
    """
    Display classification history with enhanced filtering and pagination
    """
    try:
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort', 'date-desc')
        status_filter = request.GET.get('status', 'all')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # DUMMY DATA - Replace with actual model query
        classifications_dummy = [
            {
                'id': 1,
                'filename': 'SOAL LATIHAN UTS.pdf',
                'total_questions': 21,
                'created_at': '09/11/2025',
                'q1_count': 4,
                'q2_count': 5,
                'q3_count': 4,
                'q4_count': 2,
                'q5_count': 2,
                'q6_count': 4,
                'status': 'completed',
            },
            {
                'id': 2,
                'filename': 'Soal UTS Semester Ganjil.pdf',
                'total_questions': 10,
                'created_at': '15/10/2025',
                'q1_count': 2,
                'q2_count': 2,
                'q3_count': 1,
                'q4_count': 3,
                'q5_count': 2,
                'q6_count': 0,
                'status': 'completed',
            },
            {
                'id': 3,
                'filename': 'Quiz Matematika.pdf',
                'total_questions': 15,
                'created_at': '22/09/2025',
                'q1_count': 3,
                'q2_count': 4,
                'q3_count': 2,
                'q4_count': 4,
                'q5_count': 2,
                'q6_count': 0,
                'status': 'completed',
            },
        ]
        
        # WHEN MODEL IS READY:
        """
        queryset = Classification.objects.filter(user=request.user)
        
        # Apply filters
        if search_query:
            queryset = queryset.filter(
                Q(filename__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=date_to_obj)
            except ValueError:
                pass
        
        # Apply sorting
        sort_mapping = {
            'date-desc': '-created_at',
            'date-asc': 'created_at',
            'questions-desc': '-total_questions',
            'questions-asc': 'total_questions',
            'name-asc': 'filename',
            'name-desc': '-filename',
        }
        
        order_by = sort_mapping.get(sort_by, '-created_at')
        classifications = queryset.order_by(order_by)
        
        # Calculate statistics
        stats = classifications.aggregate(
            total=Count('id'),
            total_questions=Sum('total_questions'),
            completed=Count('id', filter=Q(status='completed')),
            processing=Count('id', filter=Q(status='processing')),
            failed=Count('id', filter=Q(status='failed'))
        )
        
        last_classification = classifications.first()
        last_activity = last_classification.formatted_created_at if last_classification else 'N/A'
        """
        
        # Filter dummy data
        if search_query:
            classifications_dummy = [
                c for c in classifications_dummy 
                if search_query.lower() in c['filename'].lower()
            ]
        
        if status_filter != 'all':
            classifications_dummy = [
                c for c in classifications_dummy 
                if c['status'] == status_filter
            ]
        
        # Sort dummy data
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
        page = request.GET.get('page', 1)
        paginator = Paginator(classifications_dummy, 10)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        context = {
            'classifications': page_obj,
            'total_classifications': total_classifications,
            'total_questions': total_questions,
            'last_activity': last_activity,
            'search_query': search_query,
            'sort_by': sort_by,
            'status_filter': status_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
        
        return render(request, 'klasifikasi/history.html', context)
        
    except Exception as e:
        logger.error(f"Error in history_view: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading history.')
        return redirect('klasifikasi:home')


@login_required
@csrf_protect
@require_POST
def delete_classification(request, pk):
    """
    Delete classification with proper error handling and security
    """
    try:
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(
            Classification, 
            pk=pk, 
            user=request.user
        )
        
        filename = classification.filename
        
        # Delete the classification (files will be deleted by signal)
        classification.delete()
        
        logger.info(f"Classification {pk} ({filename}) deleted by user {request.user.username}")
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'"{filename}" deleted successfully'
            })
        
        messages.success(request, f'Classification "{filename}" deleted successfully.')
        """
        
        # DUMMY response
        logger.info(f"Classification {pk} would be deleted by user {request.user.username}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Classification deleted successfully'
            })
        
        messages.success(request, 'Classification deleted successfully.')
        return redirect('klasifikasi:history')
        
    except Http404:
        error_msg = 'Classification not found or you do not have permission to delete it.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=404)
        messages.error(request, error_msg)
        return redirect('klasifikasi:history')
        
    except Exception as e:
        logger.error(f"Error deleting classification {pk}: {str(e)}", exc_info=True)
        error_msg = 'An error occurred while deleting the classification.'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=500)
        
        messages.error(request, error_msg)
        return redirect('klasifikasi:history')


@login_required
@require_http_methods(["GET"])
def download_report(request, pk):
    """
    Download classification report with validation and security
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
            messages.error(request, 'Report file not available.')
            return redirect('klasifikasi:history')
        
        file_path = classification.result_file.path
        
        if not os.path.exists(file_path):
            messages.error(request, 'Report file not found on server.')
            return redirect('klasifikasi:history')
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Create response with file
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type
        )
        
        filename = os.path.basename(file_path)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = os.path.getsize(file_path)
        
        logger.info(
            f"Report downloaded: {classification.filename} "
            f"by {request.user.username}"
        )
        
        return response
        """
        
        messages.info(request, 'Report download functionality will be available soon.')
        return redirect('klasifikasi:history')
        
    except Exception as e:
        logger.error(f"Error downloading report {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'Error downloading report.')
        return redirect('klasifikasi:history')


@login_required
@require_http_methods(["GET"])
def get_classification_stats(request):
    """
    API endpoint for classification statistics (AJAX)
    Returns comprehensive statistics about user's classifications
    """
    try:
        # DUMMY data
        stats = {
            'total_classifications': 3,
            'total_questions': 46,
            'completed': 3,
            'processing': 0,
            'failed': 0,
            'categories': {
                'C1': 9,
                'C2': 11,
                'C3': 7,
                'C4': 9,
                'C5': 6,
                'C6': 4,
            },
            'recent_activity': [
                {
                    'id': 1,
                    'filename': 'SOAL LATIHAN UTS.pdf',
                    'date': '09/11/2025',
                    'questions': 21,
                    'status': 'completed'
                },
                {
                    'id': 2,
                    'filename': 'Soal UTS Semester Ganjil.pdf',
                    'date': '15/10/2025',
                    'questions': 10,
                    'status': 'completed'
                },
                {
                    'id': 3,
                    'filename': 'Quiz Matematika.pdf',
                    'date': '22/09/2025',
                    'questions': 15,
                    'status': 'completed'
                }
            ]
        }
        
        # WHEN MODEL IS READY:
        """
        from django.db.models import Sum, Count, Q
        
        classifications = Classification.objects.filter(user=request.user)
        
        # Aggregate statistics
        aggregates = classifications.aggregate(
            total=Count('id'),
            total_questions=Sum('total_questions'),
            completed=Count('id', filter=Q(status='completed')),
            processing=Count('id', filter=Q(status='processing')),
            failed=Count('id', filter=Q(status='failed')),
            total_c1=Sum('q1_count'),
            total_c2=Sum('q2_count'),
            total_c3=Sum('q3_count'),
            total_c4=Sum('q4_count'),
            total_c5=Sum('q5_count'),
            total_c6=Sum('q6_count'),
        )
        
        stats = {
            'total_classifications': aggregates['total'] or 0,
            'total_questions': aggregates['total_questions'] or 0,
            'completed': aggregates['completed'] or 0,
            'processing': aggregates['processing'] or 0,
            'failed': aggregates['failed'] or 0,
            'categories': {
                'C1': aggregates['total_c1'] or 0,
                'C2': aggregates['total_c2'] or 0,
                'C3': aggregates['total_c3'] or 0,
                'C4': aggregates['total_c4'] or 0,
                'C5': aggregates['total_c5'] or 0,
                'C6': aggregates['total_c6'] or 0,
            },
            'recent_activity': [
                {
                    'id': c.id,
                    'filename': c.filename,
                    'date': c.formatted_created_at,
                    'questions': c.total_questions,
                    'status': c.status
                }
                for c in classifications.order_by('-created_at')[:5]
            ]
        }
        """
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"Error fetching classification stats: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch statistics'
        }, status=500)


@login_required
@csrf_protect
@require_POST
def bulk_delete_classifications(request):
    """
    Delete multiple classifications at once
    Enhanced with transaction support and better error handling
    """
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({
                'success': False,
                'error': 'No classification IDs provided'
            }, status=400)
        
        if not isinstance(ids, list):
            return JsonResponse({
                'success': False,
                'error': 'IDs must be provided as a list'
            }, status=400)
        
        # Validate all IDs are integers
        try:
            ids = [int(id_val) for id_val in ids]
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'All IDs must be valid integers'
            }, status=400)
        
        # WHEN MODEL IS READY:
        """
        from django.db import transaction
        
        with transaction.atomic():
            classifications = Classification.objects.filter(
                pk__in=ids,
                user=request.user
            ).select_for_update()
            
            deleted_count = 0
            filenames = []
            
            for classification in classifications:
                filenames.append(classification.filename)
                classification.delete()  # Files deleted by signal
                deleted_count += 1
            
            logger.info(
                f"Bulk deleted {deleted_count} classifications by user {request.user.username}: "
                f"{', '.join(filenames[:5])}{'...' if len(filenames) > 5 else ''}"
            )
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'{deleted_count} classification(s) deleted successfully'
        })
        """
        
        # DUMMY response
        logger.info(
            f"Would bulk delete {len(ids)} classifications by user {request.user.username}"
        )
        
        return JsonResponse({
            'success': True,
            'deleted_count': len(ids),
            'message': f'{len(ids)} classification(s) deleted successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while deleting classifications'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def export_classification_excel(request, pk):
    """
    Export classification results to Excel format
    """
    try:
        # WHEN MODEL IS READY:
        """
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from django.http import HttpResponse
        from io import BytesIO
        
        classification = get_object_or_404(
            Classification,
            pk=pk,
            user=request.user
        )
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Classification Results"
        
        # Define styles
        header_fill = PatternFill(start_color="2B579A", end_color="2B579A", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Add headers
        headers = ['No', 'Question', 'Category', 'Level Name', 'Confidence', 'Manually Classified']
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border
        
        # Add data
        questions = classification.questions.all().order_by('question_number')
        for row_num, question in enumerate(questions, 2):
            ws.cell(row=row_num, column=1, value=question.question_number).border = border
            ws.cell(row=row_num, column=2, value=question.question_text).border = border
            ws.cell(row=row_num, column=3, value=question.category).border = border
            ws.cell(row=row_num, column=4, value=question.category_name).border = border
            ws.cell(row=row_num, column=5, value=question.formatted_confidence).border = border
            ws.cell(row=row_num, column=6, value='Yes' if question.is_manually_classified else 'No').border = border
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 80
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 12
        ws.column_dimensions['F'].width = 18
        
        # Save to response
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"classification_{classification.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Excel export: {classification.filename} by {request.user.username}")
        
        return response
        """
        
        messages.info(request, 'Excel export functionality will be available soon.')
        return redirect('klasifikasi:hasil_klasifikasi', pk=pk)
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}", exc_info=True)
        messages.error(request, 'Error exporting to Excel.')
        return redirect('klasifikasi:hasil_klasifikasi', pk=pk)


@login_required
@require_http_methods(["GET"])
def get_question_details(request, classification_id, question_id):
    """
    API endpoint to get detailed information about a specific question
    """
    try:
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(
            Classification,
            pk=classification_id,
            user=request.user
        )
        
        question = get_object_or_404(
            Question,
            pk=question_id,
            classification=classification
        )
        
        data = {
            'id': question.id,
            'number': question.question_number,
            'text': question.question_text,
            'category': question.category,
            'category_name': question.category_name,
            'category_description': question.category_description,
            'confidence': question.confidence_score,
            'formatted_confidence': question.formatted_confidence,
            'is_manually_classified': question.is_manually_classified,
            'previous_category': question.previous_category,
            'has_choices': question.has_choices,
            'choices': question.choices_list if question.has_choices else [],
            'correct_answer': question.correct_answer,
            'created_at': question.created_at.isoformat(),
            'updated_at': question.updated_at.isoformat()
        }
        
        return JsonResponse(data)
        """
        
        # DUMMY response
        return JsonResponse({
            'id': question_id,
            'number': 1,
            'text': 'Sample question text',
            'category': 'C1',
            'category_name': 'Remember',
            'confidence': 0.95,
            'is_manually_classified': False
        })
        
    except Exception as e:
        logger.error(f"Error fetching question details: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch question details'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def classification_analytics(request, pk):
    """
    Display detailed analytics for a classification
    """
    try:
        # WHEN MODEL IS READY:
        """
        classification = get_object_or_404(
            Classification,
            pk=pk,
            user=request.user
        )
        
        # Get distribution data
        distribution = classification.distribution_percentages
        
        # Get question confidence statistics
        questions = classification.questions.all()
        avg_confidence = questions.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
        
        # Get manually classified count
        manual_count = questions.filter(is_manually_classified=True).count()
        
        context = {
            'classification': classification,
            'distribution': distribution,
            'avg_confidence': avg_confidence * 100,
            'manual_count': manual_count,
            'auto_count': classification.total_questions - manual_count
        }
        
        return render(request, 'klasifikasi/analytics.html', context)
        """
        
        messages.info(request, 'Analytics page will be available soon.')
        return redirect('klasifikasi:hasil_klasifikasi', pk=pk)
        
    except Exception as e:
        logger.error(f"Error loading analytics: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading analytics.')
        return redirect('klasifikasi:history')