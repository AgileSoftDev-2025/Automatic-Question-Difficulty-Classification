# apps/klasifikasi/views.py

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
import mimetypes
import logging

# Import ML model classifier
from .ml_model import classify_questions_batch, get_classifier, classify_question

# Import file extractor
from .file_extractor import QuestionExtractor, extract_questions_from_file

# Import ClassificationHistory model
from apps.soal.models import ClassificationHistory

logger = logging.getLogger(__name__)

# Imports for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from io import BytesIO


def redirect_to_main_home(request):
    """Redirect /klasifikasi/ to main home page"""
    return redirect('soal:home')


@login_required
@require_http_methods(["GET"])
def hasil_klasifikasi(request, pk=None):
    """
    Display classification results page with ML model predictions
    """
    try:
        # Get classification from database
        classification = get_object_or_404(
            ClassificationHistory,
            pk=pk,
            user=request.user
        )
        
        # Check if classification is completed
        if classification.status == 'pending':
            messages.info(request, 'Classification is pending. Processing will start shortly.')
            return redirect('soal:home')
        elif classification.status == 'processing':
            messages.info(request, 'Classification is in progress. Please wait...')
            return redirect('soal:home')
        elif classification.status == 'failed':
            messages.error(request, 'Classification failed. Please try uploading the file again.')
            return redirect('soal:home')
        
        # Get classification results from JSON field
        if not classification.classification_results:
            messages.error(request, 'No classification results available.')
            return redirect('soal:home')
        
        results = classification.classification_results
        questions_data = results.get('questions', [])
        category_counts = results.get('category_counts', {})
        
        # Build questions data for template
        formatted_questions = []
        for q in questions_data:
            formatted_questions.append({
                'question': q['question_text'],
                'level': q['category'],
                'index': q['question_number'],
                'confidence': q['confidence'] * 100  # Convert to percentage
            })
        
        context = {
            'filename': classification.filename,
            'file_url': classification.file_url or '#',
            'questions': formatted_questions,
            'labels': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
            'total_questions': classification.total_questions,
            'classification_id': pk,
            'classification_date': classification.created_at.strftime('%d/%m/%Y'),
            'category_counts': category_counts,
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
    """
    try:
        data = json.loads(request.body)
        question_number = data.get('question_number')
        new_category = data.get('category')
        
        if not question_number or not new_category:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)
        
        valid_categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        if new_category not in valid_categories:
            return JsonResponse({
                'success': False,
                'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            }, status=400)
        
        # Get classification
        classification = get_object_or_404(ClassificationHistory, pk=pk, user=request.user)
        
        if not classification.classification_results:
            return JsonResponse({
                'success': False,
                'error': 'No classification results found'
            }, status=404)
        
        # Update the specific question
        results = classification.classification_results
        questions = results.get('questions', [])
        
        # Find and update the question
        question_found = False
        old_category = None
        
        for q in questions:
            if q['question_number'] == question_number:
                old_category = q['category']
                q['category'] = new_category
                q['manually_modified'] = True
                question_found = True
                break
        
        if not question_found:
            return JsonResponse({
                'success': False,
                'error': 'Question not found'
            }, status=404)
        
        # Update category counts
        category_counts = results.get('category_counts', {})
        if old_category in category_counts:
            category_counts[old_category] -= 1
        category_counts[new_category] = category_counts.get(new_category, 0) + 1
        
        # Save updated results
        results['questions'] = questions
        results['category_counts'] = category_counts
        classification.classification_results = results
        classification.save()
        
        logger.info(
            f"Question {question_number} updated from {old_category} to {new_category} "
            f"by user {request.user.username} in classification {pk}"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Classification updated successfully',
            'question_number': question_number,
            'new_category': new_category,
            'old_category': old_category
        })
        
    except Exception as e:
        logger.error(f"Error updating question classification: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An internal error occurred'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def history_view(request):
    """Display classification history using real database data"""
    try:
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort', 'date-desc')
        
        # Query classifications from database
        classifications = ClassificationHistory.objects.filter(
            user=request.user
        ).select_related('user')
        
        # Apply search filter
        if search_query:
            classifications = classifications.filter(
                Q(filename__icontains=search_query)
            )
        
        # Apply sorting
        if sort_by == 'date-desc':
            classifications = classifications.order_by('-created_at')
        elif sort_by == 'date-asc':
            classifications = classifications.order_by('created_at')
        elif sort_by == 'name-asc':
            classifications = classifications.order_by('filename')
        elif sort_by == 'name-desc':
            classifications = classifications.order_by('-filename')
        
        # Calculate statistics
        total_classifications = classifications.count()
        total_questions = classifications.filter(
            status='completed'
        ).aggregate(Sum('total_questions'))['total_questions__sum'] or 0
        
        last_classification = classifications.order_by('-created_at').first()
        last_activity = last_classification.created_at.strftime('%d/%m/%Y') if last_classification else 'N/A'
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(classifications, 10)
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        # Format data for template
        formatted_classifications = []
        for c in page_obj:
            # Get category counts from classification results
            category_counts = {}
            if c.classification_results:
                category_counts = c.classification_results.get('category_counts', {})
            
            formatted_classifications.append({
                'id': c.id,
                'filename': c.filename,
                'total_questions': c.total_questions,
                'created_at': c.created_at.strftime('%d/%m/%Y'),
                'q1_count': category_counts.get('C1', 0),
                'q2_count': category_counts.get('C2', 0),
                'q3_count': category_counts.get('C3', 0),
                'q4_count': category_counts.get('C4', 0),
                'q5_count': category_counts.get('C5', 0),
                'q6_count': category_counts.get('C6', 0),
                'status': c.status,
            })
        
        context = {
            'classifications': formatted_classifications,
            'page_obj': page_obj,
            'total_classifications': total_classifications,
            'total_questions': total_questions,
            'last_activity': last_activity,
            'search_query': search_query,
            'sort_by': sort_by,
        }
        
        return render(request, 'klasifikasi/history.html', context)
        
    except Exception as e:
        logger.error(f"Error in history_view: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading history.')
        return redirect('soal:home')


@login_required
@csrf_protect
@require_POST
def delete_classification(request, pk):
    """Delete classification with proper error handling"""
    try:
        classification = get_object_or_404(
            ClassificationHistory, 
            pk=pk, 
            user=request.user
        )
        
        filename = classification.filename
        
        # Delete physical file
        if classification.file_path:
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', classification.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
                except OSError as e:
                    logger.warning(f"Could not delete file {file_path}: {str(e)}")
        
        # Delete database record
        classification.delete()
        
        logger.info(f"Classification {pk} ({filename}) deleted by user {request.user.username}")
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'"{filename}" deleted successfully'
            })
        
        messages.success(request, f'Classification "{filename}" deleted successfully.')
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


def add_page_number(canvas_obj, doc):
    """Add page numbers to PDF"""
    page_num = canvas_obj.getPageNumber()
    text = f"Page {page_num}"
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 9)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawRightString(
        letter[0] - 0.75 * inch,
        0.5 * inch,
        text
    )
    canvas_obj.restoreState()


@login_required
@require_http_methods(["GET"])
def download_report(request, pk):
    """Download classification report as PDF using real data"""
    try:
        classification = get_object_or_404(
            ClassificationHistory, 
            pk=pk, 
            user=request.user
        )
        
        if classification.status != 'completed':
            messages.error(request, 'Classification is not yet completed.')
            return redirect('klasifikasi:history')
        
        if not classification.classification_results:
            messages.error(request, 'No classification results available.')
            return redirect('klasifikasi:history')
        
        results = classification.classification_results
        questions_data = results.get('questions', [])
        category_counts = results.get('category_counts', {})
        
        # Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#374151'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6,
        )
        
        # Title
        title = Paragraph("BLOOMERS Classification Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Report Information
        info_data = [
            ['File Name:', classification.filename],
            ['Classification ID:', f"#{classification.id}"],
            ['Generated On:', classification.created_at.strftime('%d/%m/%Y %H:%M')],
            ['Total Questions:', str(classification.total_questions)],
            ['User:', request.user.username],
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#6b7280')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Distribution Summary
        elements.append(Paragraph("Classification Distribution", heading_style))
        
        total = classification.total_questions
        distribution_data = [
            ['Category', 'Level', 'Count', 'Percentage'],
            ['C1', 'Remember', str(category_counts.get('C1', 0)), 
             f"{(category_counts.get('C1', 0)/total*100):.1f}%" if total > 0 else "0%"],
            ['C2', 'Understand', str(category_counts.get('C2', 0)), 
             f"{(category_counts.get('C2', 0)/total*100):.1f}%" if total > 0 else "0%"],
            ['C3', 'Apply', str(category_counts.get('C3', 0)), 
             f"{(category_counts.get('C3', 0)/total*100):.1f}%" if total > 0 else "0%"],
            ['C4', 'Analyze', str(category_counts.get('C4', 0)), 
             f"{(category_counts.get('C4', 0)/total*100):.1f}%" if total > 0 else "0%"],
            ['C5', 'Evaluate', str(category_counts.get('C5', 0)), 
             f"{(category_counts.get('C5', 0)/total*100):.1f}%" if total > 0 else "0%"],
            ['C6', 'Create', str(category_counts.get('C6', 0)), 
             f"{(category_counts.get('C6', 0)/total*100):.1f}%" if total > 0 else "0%"],
        ]
        
        dist_table = Table(distribution_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.5*inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(dist_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Questions Detail
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Question Classification", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        category_colors = {
            'C1': colors.HexColor('#dcfce7'),
            'C2': colors.HexColor('#dbeafe'),
            'C3': colors.HexColor('#fef3c7'),
            'C4': colors.HexColor('#fed7aa'),
            'C5': colors.HexColor('#fecaca'),
            'C6': colors.HexColor('#e9d5ff'),
        }
        
        for question in questions_data:
            q_header = Paragraph(
                f"<b>Question {question['question_number']}</b> - "
                f"Category: {question['category']} | "
                f"Confidence: {question['confidence']*100:.1f}%",
                subheading_style
            )
            
            q_text = Paragraph(question['question_text'], normal_style)
            
            q_data = [[q_header], [q_text]]
            q_table = Table(q_data, colWidths=[6*inch])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), category_colors.get(question['category'], colors.lightgrey)),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(KeepTogether([q_table, Spacer(1, 0.15*inch)]))
        
        # Footer
        elements.append(PageBreak())
        elements.append(Spacer(1, 0.5*inch))
        
        footer_text = Paragraph(
            "<b>About Bloom's Taxonomy Levels:</b><br/><br/>"
            "<b>C1 (Remember):</b> Recall facts and basic concepts<br/>"
            "<b>C2 (Understand):</b> Explain ideas or concepts<br/>"
            "<b>C3 (Apply):</b> Use information in new situations<br/>"
            "<b>C4 (Analyze):</b> Draw connections among ideas<br/>"
            "<b>C5 (Evaluate):</b> Justify a decision or course of action<br/>"
            "<b>C6 (Create):</b> Produce new or original work<br/><br/>"
            "<i>This report was automatically generated by BLOOMERS Classification System.</i>",
            normal_style
        )
        elements.append(footer_text)
        
        # Build PDF
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"classification_report_{pk}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Report downloaded: Classification {pk} by {request.user.username}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating report {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'Error generating report. Please try again.')
        return redirect('klasifikasi:history')


@login_required
@require_http_methods(["GET"])
def get_classification_stats(request):
    """API endpoint for classification statistics (AJAX)"""
    try:
        classifications = ClassificationHistory.objects.filter(user=request.user)
        
        aggregates = classifications.aggregate(
            total=Count('id'),
            total_questions=Sum('total_questions'),
            completed=Count('id', filter=Q(status='completed')),
            processing=Count('id', filter=Q(status='processing')),
            failed=Count('id', filter=Q(status='failed')),
        )
        
        # Calculate category totals
        category_totals = {'C1': 0, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'C6': 0}
        for c in classifications.filter(status='completed'):
            if c.classification_results:
                counts = c.classification_results.get('category_counts', {})
                for cat in category_totals.keys():
                    category_totals[cat] += counts.get(cat, 0)
        
        # Recent activity
        recent = classifications.order_by('-created_at')[:5]
        recent_activity = [
            {
                'id': c.id,
                'filename': c.filename,
                'date': c.created_at.strftime('%d/%m/%Y'),
                'questions': c.total_questions,
                'status': c.status
            }
            for c in recent
        ]
        
        stats = {
            'total_classifications': aggregates['total'] or 0,
            'total_questions': aggregates['total_questions'] or 0,
            'completed': aggregates['completed'] or 0,
            'processing': aggregates['processing'] or 0,
            'failed': aggregates['failed'] or 0,
            'categories': category_totals,
            'recent_activity': recent_activity
        }
        
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
    """Delete multiple classifications at once"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids or not isinstance(ids, list):
            return JsonResponse({
                'success': False,
                'error': 'Invalid or missing IDs'
            }, status=400)
        
        try:
            ids = [int(id_val) for id_val in ids]
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'All IDs must be valid integers'
            }, status=400)
        
        classifications = ClassificationHistory.objects.filter(
            pk__in=ids,
            user=request.user
        )
        
        deleted_count = 0
        for classification in classifications:
            # Delete file
            if classification.file_path:
                file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', classification.file_path)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        logger.warning(f"Could not delete file {file_path}: {str(e)}")
            
            classification.delete()
            deleted_count += 1
        
        logger.info(f"Bulk deleted {deleted_count} classifications by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'{deleted_count} classification(s) deleted successfully'
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