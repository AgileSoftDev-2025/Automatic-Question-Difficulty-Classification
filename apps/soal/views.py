# apps/soal/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, FileResponse, Http404
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
import os
import uuid
import mimetypes
import logging
from pathlib import Path

from .models import ClassificationHistory

# Import ML and extraction functionality
from apps.klasifikasi.ml_model import classify_questions_batch, get_classifier
from apps.klasifikasi.file_extractor import QuestionExtractor

# Configure logging
logger = logging.getLogger(__name__)

# File configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
TEMP_FILE_CACHE_TIMEOUT = 3600  # 1 hour


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size_mb(file):
    """Get file size in megabytes."""
    return file.size / (1024 * 1024)


def validate_file(uploaded_file):
    """
    Validate uploaded file for type and size.
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not uploaded_file:
        return False, "No file selected. Please choose a file to upload."
    
    # Check file extension
    if not allowed_file(uploaded_file.name):
        allowed_str = ', '.join(ext.upper() for ext in ALLOWED_EXTENSIONS)
        return False, f"Invalid file type. Allowed formats: {allowed_str}"
    
    # Check file size
    file_size_mb = get_file_size_mb(uploaded_file)
    max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.2f}MB) exceeds the maximum limit of {max_size_mb:.0f}MB."
    
    # Check if file is empty
    if uploaded_file.size == 0:
        return False, "The uploaded file is empty. Please upload a valid file."
    
    return True, None


def help_faq(request):
    """Render help/FAQ page."""
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'soal/help.html', context)


def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent overwriting."""
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    safe_name = original_filename.rsplit('.', 1)[0][:50]  # Limit name length
    return f"{uuid.uuid4().hex}_{safe_name}.{file_extension}"


@require_http_methods(["GET", "POST"])
def home(request):
    """
    Home page with file upload functionality.
    Handles both authenticated and anonymous users.
    """
    context = {
        'is_authenticated': request.user.is_authenticated,
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
        'allowed_extensions': ', '.join(sorted(ALLOWED_EXTENSIONS)).upper()
    }
    
    if request.method == 'POST':
        return handle_file_upload(request, context)
    
    # GET request - populate context with user history
    if request.user.is_authenticated:
        try:
            # Get recent history with efficient query
            context['history'] = ClassificationHistory.objects.filter(
                user=request.user
            ).select_related('user').order_by('-created_at')[:10]
            
            # Get statistics
            stats = ClassificationHistory.objects.filter(
                user=request.user
            ).aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                processing=Count('id', filter=Q(status='processing')),
                failed=Count('id', filter=Q(status='failed'))
            )
            
            context.update({
                'total_files': stats['total'],
                'completed_files': stats['completed'],
                'processing_files': stats['processing'],
                'failed_files': stats['failed']
            })
            
        except Exception as e:
            logger.error(f"Error loading user history: {str(e)}", exc_info=True)
            messages.warning(request, "Unable to load history. Please refresh the page.")
    
    return render(request, 'soal/home.html', context)


def handle_file_upload(request, context):
    """Handle file upload logic for both authenticated and anonymous users."""
    uploaded_file = request.FILES.get('file')
    
    # Validate file
    is_valid, error_message = validate_file(uploaded_file)
    if not is_valid:
        messages.error(request, error_message)
        logger.warning(f"File validation failed: {error_message}")
        return redirect('soal:home')
    
    try:
        if request.user.is_authenticated:
            return handle_authenticated_upload(request, uploaded_file)
        else:
            return handle_anonymous_upload(request, uploaded_file)
            
    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while uploading your file. Please try again.")
        return redirect('soal:home')


def handle_authenticated_upload(request, uploaded_file):
    """
    Handle file upload for authenticated users.
    Saves file permanently and creates database record.
    """
    # Setup file storage
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    
    fs = FileSystemStorage(location=upload_path)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(uploaded_file.name)
    
    # Save file
    try:
        saved_filename = fs.save(unique_filename, uploaded_file)
        file_url = fs.url(saved_filename)
        
        logger.info(f"File saved: {saved_filename}")
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}", exc_info=True)
        messages.error(request, "Failed to save the file. Please try again.")
        return redirect('soal:home')
    
    # Create classification history record
    try:
        history = ClassificationHistory.objects.create(
            user=request.user,
            filename=uploaded_file.name,
            file_path=saved_filename,
            file_url=file_url,
            file_size=uploaded_file.size,
            status='pending'
        )
        
        logger.info(f"File uploaded successfully: {uploaded_file.name} by user {request.user.username}")
        messages.success(
            request, 
            f'✓ File "{uploaded_file.name}" uploaded successfully! Click "Start Classification" to begin.'
        )
        
        # Process the file immediately in synchronous mode
        # In production, you would use Celery/background task
        process_classification_sync(history.id)
        
    except Exception as e:
        # Cleanup file if database record creation fails
        try:
            file_path = os.path.join(upload_path, saved_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file after DB error: {file_path}")
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")
        
        logger.error(f"Error creating classification record: {str(e)}", exc_info=True)
        messages.error(request, "Failed to create classification record. Please try again.")
    
    return redirect('soal:home')


def process_classification_sync(history_id):
    """
    Process classification synchronously.
    In production, this should be a Celery task.
    """
    try:
        history = ClassificationHistory.objects.get(id=history_id)
        history.mark_as_processing()
        
        # Get file path
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', history.file_path)
        
        # Extract questions
        logger.info(f"Extracting questions from: {file_path}")
        extractor = QuestionExtractor()
        questions = extractor.extract_questions(file_path)
        
        # Validate questions
        validation = extractor.validate_questions(questions)
        if not validation['valid']:
            logger.error(f"Question validation failed: {validation['error']}")
            history.mark_as_failed()
            return
        
        logger.info(f"Extracted {len(questions)} questions")
        
        # Classify questions using ML model
        logger.info("Starting ML classification...")
        predictions = classify_questions_batch(
            questions,
            translate=True,
            batch_size=8
        )
        
        # Apply Indonesian pattern-based adjustments
        logger.info("Applying Indonesian pattern adjustments...")
        from apps.klasifikasi.indonesian_rules import adjust_classification_with_patterns
        
        adjusted_predictions = []
        for question, pred in zip(questions, predictions):
            adjusted = adjust_classification_with_patterns(question, pred)
            adjusted_predictions.append(adjusted)
        
        # Build classification results
        results = []
        category_counts = {'C1': 0, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'C6': 0}
        
        for i, (question, pred) in enumerate(zip(questions, adjusted_predictions), 1):
            # Convert all_probabilities to JSON-serializable format
            serializable_probs = {}
            for label, prob_data in pred['all_probabilities'].items():
                serializable_probs[label] = {
                    'probability': float(prob_data['probability']),
                    'predicted': bool(prob_data['predicted'])  # Ensure it's a Python bool
                }
            
            result = {
                'question_number': i,
                'question_text': question,
                'category': pred['category'],
                'category_name': pred['category_name'],
                'confidence': float(pred['confidence']),  # Ensure it's a Python float
                'all_probabilities': serializable_probs,
                'was_adjusted': pred.get('adjustment_reason', 'none') != 'ml_prediction_kept'
            }
            results.append(result)
            category_counts[pred['category']] += 1
        
        # Save results
        classification_data = {
            'questions': results,
            'category_counts': category_counts,
            'total_questions': len(questions)
        }
        
        history.mark_as_completed(
            results=classification_data,
            total_questions=len(questions)
        )
        
        logger.info(f"Classification completed for history {history_id}")
        
    except Exception as e:
        logger.error(f"Error processing classification {history_id}: {str(e)}", exc_info=True)
        try:
            history = ClassificationHistory.objects.get(id=history_id)
            history.mark_as_failed()
        except:
            pass


def handle_anonymous_upload(request, uploaded_file):
    """
    Handle file upload for anonymous users.
    Stores file temporarily in cache.
    """
    cache_key = f'temp_file_{uuid.uuid4().hex}'
    
    try:
        # Store file data in cache
        cache.set(cache_key, {
            'filename': uploaded_file.name,
            'content': uploaded_file.read(),
            'size': uploaded_file.size,
            'uploaded_at': timezone.now().isoformat()
        }, timeout=TEMP_FILE_CACHE_TIMEOUT)
        
        logger.info(f"Temporary file cached: {uploaded_file.name}")
        messages.success(
            request,
            f'✓ File "{uploaded_file.name}" uploaded successfully! '
            'Note: Please log in to save your classification history permanently.'
        )
        messages.info(
            request,
            'Your file will be available for 1 hour. Log in to keep your results longer.'
        )
        
    except Exception as e:
        logger.error(f"Error caching temporary file: {str(e)}", exc_info=True)
        messages.error(request, "Failed to process your file. Please try again.")
    
    return redirect('soal:home')


@login_required
@require_http_methods(["GET", "POST"])
def delete_history(request, history_id):
    """Delete a classification history entry and associated file."""
    history = get_object_or_404(
        ClassificationHistory, 
        id=history_id, 
        user=request.user
    )
    
    filename = history.filename
    
    try:
        # Delete the physical file
        if history.file_path:
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', history.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
                except OSError as e:
                    logger.warning(f"Could not delete file {file_path}: {str(e)}")
        
        # Delete database record
        history.delete()
        
        logger.info(f"Deleted history record {history_id} for user {request.user.username}")
        messages.success(request, f'✓ "{filename}" has been deleted successfully.')
        
    except Exception as e:
        logger.error(f"Error deleting history {history_id}: {str(e)}", exc_info=True)
        messages.error(request, f'Failed to delete "{filename}". Please try again.')
    
    return redirect('soal:home')


@login_required
def download_file(request, history_id):
    """Download a previously uploaded file."""
    history = get_object_or_404(
        ClassificationHistory, 
        id=history_id, 
        user=request.user
    )
    
    if not history.file_path:
        logger.warning(f"File path not found for history {history_id}")
        raise Http404("File not found")
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', history.file_path)
    
    if not os.path.exists(file_path):
        logger.error(f"Physical file missing: {file_path}")
        messages.error(request, "File no longer exists on server.")
        return redirect('soal:home')
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    try:
        response = FileResponse(
            open(file_path, 'rb'), 
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{history.filename}"'
        
        logger.info(f"File downloaded: {history.filename} by user {request.user.username}")
        return response
        
    except Exception as e:
        logger.error(f"Error downloading file {history_id}: {str(e)}", exc_info=True)
        messages.error(request, 'Error downloading file. Please try again.')
        return redirect('soal:home')


@login_required
@require_http_methods(["POST"])
def clear_all_history(request):
    """
    Clear all classification history for the current user.
    Deletes all files and database records.
    """
    try:
        histories = ClassificationHistory.objects.filter(user=request.user)
        count = histories.count()
        
        if count == 0:
            messages.info(request, "No history to clear.")
            return redirect('soal:home')
        
        # Delete all physical files
        deleted_files = 0
        for history in histories:
            if history.file_path:
                file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', history.file_path)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                    except OSError as e:
                        logger.warning(f"Could not delete file {file_path}: {str(e)}")
        
        # Delete all database records
        histories.delete()
        
        logger.info(
            f"Cleared {count} history records ({deleted_files} files) "
            f"for user {request.user.username}"
        )
        messages.success(
            request, 
            f'✓ Successfully deleted {count} file(s) from your history.'
        )
        
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}", exc_info=True)
        messages.error(request, 'Error clearing history. Please try again.')
    
    return redirect('soal:home')


@require_http_methods(["POST"])
def validate_file_ajax(request):
    """
    AJAX endpoint to validate file before upload.
    Useful for client-side validation feedback.
    """
    uploaded_file = request.FILES.get('file')
    
    is_valid, error_message = validate_file(uploaded_file)
    
    if is_valid:
        return JsonResponse({
            'valid': True,
            'filename': uploaded_file.name,
            'size_mb': round(get_file_size_mb(uploaded_file), 2),
            'size_bytes': uploaded_file.size,
            'extension': uploaded_file.name.rsplit('.', 1)[1].lower(),
            'message': 'File is valid and ready to upload.'
        })
    else:
        return JsonResponse({
            'valid': False,
            'message': error_message
        }, status=400)