# apps/klasifikasi/views.py - COMPLETE FUNCTIONAL VERSION

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.conf import settings
import os
import json
from datetime import datetime, timedelta
import mimetypes
import logging

# Import ML model classifier
from .ml_model import classify_questions_batch, get_classifier, classify_question
from .file_extractor import QuestionExtractor, extract_questions_from_file
from apps.soal.models import ClassificationHistory

logger = logging.getLogger(__name__)

# PDF generation imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, KeepTogether, Image
)
from io import BytesIO

# For chart generation
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np


def redirect_to_main_home(request):
    """Redirect /klasifikasi/ to main home page"""
    return redirect('soal:home')


@login_required
@require_http_methods(["GET"])
def hasil_klasifikasi(request, pk=None):
    """Display classification results with real data from database"""
    try:
        classification = get_object_or_404(
            ClassificationHistory,
            pk=pk,
            user=request.user
        )
        
        # Check status
        if classification.status == 'pending':
            messages.info(request, 'Classification is pending. Processing will start shortly.')
            return redirect('soal:home')
        elif classification.status == 'processing':
            messages.info(request, 'Classification is in progress. Please wait and refresh the page.')
            return redirect('soal:home')
        elif classification.status == 'failed':
            messages.error(request, 'Classification failed. Please try uploading the file again.')
            return redirect('soal:home')
        
        # Get results
        if not classification.classification_results:
            messages.error(request, 'No classification results available.')
            return redirect('soal:home')
        
        results = classification.classification_results
        questions_data = results.get('questions', [])
        category_counts = results.get('category_counts', {})
        
        # Format questions for template
        formatted_questions = []
        for q in questions_data:
            formatted_questions.append({
                'question': q['question_text'],
                'level': q['category'],
                'index': q['question_number'],
                'confidence': q['confidence'] * 100,
                'was_adjusted': q.get('was_adjusted', False)
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
    """AJAX endpoint to update individual question classification"""
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
        
        classification = get_object_or_404(ClassificationHistory, pk=pk, user=request.user)
        
        if not classification.classification_results:
            return JsonResponse({
                'success': False,
                'error': 'No classification results found'
            }, status=404)
        
        results = classification.classification_results
        questions = results.get('questions', [])
        
        # Find and update question
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
            category_counts[old_category] = max(0, category_counts[old_category] - 1)
        category_counts[new_category] = category_counts.get(new_category, 0) + 1
        
        # Save
        results['questions'] = questions
        results['category_counts'] = category_counts
        classification.classification_results = results
        classification.save()
        
        logger.info(
            f"Question {question_number} updated from {old_category} to {new_category} "
            f"by {request.user.username} in classification {pk}"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Classification updated successfully',
            'question_number': question_number,
            'new_category': new_category,
            'old_category': old_category,
            'updated_counts': category_counts
        })
        
    except Exception as e:
        logger.error(f"Error updating question: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An internal error occurred'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def history_view(request):
    """Display classification history with real database data"""
    try:
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort', 'date-desc')
        
        classifications = ClassificationHistory.objects.filter(
            user=request.user
        ).select_related('user')
        
        # Search filter
        if search_query:
            classifications = classifications.filter(
                Q(filename__icontains=search_query)
            )
        
        # Sorting
        if sort_by == 'date-desc':
            classifications = classifications.order_by('-created_at')
        elif sort_by == 'date-asc':
            classifications = classifications.order_by('created_at')
        elif sort_by == 'name-asc':
            classifications = classifications.order_by('filename')
        elif sort_by == 'name-desc':
            classifications = classifications.order_by('-filename')
        elif sort_by == 'questions-desc':
            classifications = classifications.order_by('-total_questions')
        elif sort_by == 'questions-asc':
            classifications = classifications.order_by('total_questions')
        
        # Statistics
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
        
        # Format for template
        formatted_classifications = []
        for c in page_obj:
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
    """Delete classification with file cleanup"""
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
        
        classification.delete()
        
        logger.info(f"Classification {pk} ({filename}) deleted by {request.user.username}")
        
        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'"{filename}" deleted successfully'
            })
        
        messages.success(request, f'Classification "{filename}" deleted successfully.')
        return redirect('klasifikasi:history')
        
    except Http404:
        error_msg = 'Classification not found or access denied.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=404)
        messages.error(request, error_msg)
        return redirect('klasifikasi:history')
        
    except Exception as e:
        logger.error(f"Error deleting classification {pk}: {str(e)}", exc_info=True)
        error_msg = 'An error occurred while deleting.'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=500)
        
        messages.error(request, error_msg)
        return redirect('klasifikasi:history')


def generate_bar_chart(category_counts, total_questions):
    """
    Generate a beautiful bar chart for Bloom's Taxonomy distribution
    Returns: BytesIO object containing PNG image
    """
    try:
        # Prepare data
        categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        category_names = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
        counts = [category_counts.get(cat, 0) for cat in categories]
        
        # Colors matching your web interface
        colors_hex = ['#10b981', '#3b82f6', '#f59e0b', '#f97316', '#ef4444', '#a855f7']
        
        # Create figure with better styling
        fig, ax = plt.subplots(figsize=(10, 5.5))
        fig.patch.set_facecolor('white')
        
        # Create bars with gradient effect
        bars = ax.bar(range(len(categories)), counts, color=colors_hex, 
                      alpha=0.85, edgecolor='white', linewidth=2.5)
        
        # Customize chart
        ax.set_xlabel('Bloom\'s Taxonomy Levels', fontsize=13, fontweight='bold', 
                      color='#374151', labelpad=10)
        ax.set_ylabel('Number of Questions', fontsize=13, fontweight='bold', 
                      color='#374151', labelpad=10)
        ax.set_title('Question Distribution by Cognitive Level', 
                    fontsize=16, fontweight='bold', color='#1e40af', pad=20)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels([f'{cat}\n{name}' for cat, name in zip(categories, category_names)], 
                           fontsize=10, fontweight='600')
        
        # Style the axis
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['bottom'].set_color('#cbd5e1')
        ax.tick_params(colors='#64748b', labelsize=10)
        
        # Add value labels on bars with better styling
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            percentage = (count / total_questions * 100) if total_questions > 0 else 0
            ax.text(bar.get_x() + bar.get_width()/2., height + (max(counts) * 0.02),
                   f'{count}\n({percentage:.1f}%)',
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   color='#374151')
        
        # Add elegant grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.25, color='#cbd5e1', linewidth=1)
        ax.set_axisbelow(True)
        
        # Set y-axis to start from 0
        ax.set_ylim(bottom=0, top=max(counts) * 1.25 if counts else 10)
        
        plt.tight_layout()
        
        # Save to BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=180, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        logger.error(f"Error generating bar chart: {str(e)}", exc_info=True)
        return None


def generate_doughnut_chart(category_counts, total_questions):
    """
    Generate a beautiful doughnut chart for Bloom's Taxonomy distribution
    Returns: BytesIO object containing PNG image
    """
    try:
        # Prepare data
        categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        category_names = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
        counts = [category_counts.get(cat, 0) for cat in categories]
        
        # Filter out zero values
        filtered_data = [(cat, name, count) for cat, name, count in zip(categories, category_names, counts) if count > 0]
        
        if not filtered_data:
            # Return empty chart if no data
            fig, ax = plt.subplots(figsize=(6, 6))
            fig.patch.set_facecolor('white')
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   fontsize=14, color='#9ca3af')
            ax.axis('off')
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=180, bbox_inches='tight', facecolor='white')
            img_buffer.seek(0)
            plt.close(fig)
            return img_buffer
        
        categories_filtered = [item[0] for item in filtered_data]
        names_filtered = [item[1] for item in filtered_data]
        counts_filtered = [item[2] for item in filtered_data]
        
        # Colors matching your web interface
        color_map = {
            'C1': '#10b981',
            'C2': '#3b82f6',
            'C3': '#f59e0b',
            'C4': '#f97316',
            'C5': '#ef4444',
            'C6': '#a855f7'
        }
        colors_filtered = [color_map[cat] for cat in categories_filtered]
        
        # Create figure with better proportions
        fig, ax = plt.subplots(figsize=(7, 5.5))
        fig.patch.set_facecolor('white')
        
        # Create beautiful doughnut chart with shadow effect
        wedges, texts, autotexts = ax.pie(
            counts_filtered,
            labels=[f'{cat} - {name}' for cat, name in zip(categories_filtered, names_filtered)],
            colors=colors_filtered,
            autopct=lambda pct: f'{pct:.1f}%\n({int(pct*total_questions/100)})' if pct > 3 else '',
            startangle=90,
            pctdistance=0.82,
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=3, 
                          antialiased=True),
            explode=[0.03] * len(counts_filtered),  # Slight separation
            shadow=False
        )
        
        # Beautify labels
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('600')
            text.set_color('#374151')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax.set_title('Question Type Distribution', 
                    fontsize=16, fontweight='bold', color='#1e40af', pad=20)
        
        plt.tight_layout()
        
        # Save to BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=180, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        logger.error(f"Error generating doughnut chart: {str(e)}", exc_info=True)
        return None


def generate_summary_chart(category_counts, total_questions):
    """
    Generate a beautiful combined visualization with LOTS vs HOTS
    Returns: BytesIO object containing PNG image
    """
    try:
        # Calculate LOTS and HOTS
        lots = category_counts.get('C1', 0) + category_counts.get('C2', 0)
        hots = sum(category_counts.get(f'C{i}', 0) for i in range(3, 7))
        
        # Create figure with refined layout
        fig = plt.figure(figsize=(10, 4.5))
        fig.patch.set_facecolor('white')
        
        # Create grid spec for better control
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2], wspace=0.3)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        
        # Left: LOTS vs HOTS - Beautiful pie chart
        lots_hots_data = [lots, hots]
        lots_hots_labels = ['Lower Order\nThinking\n(C1-C2)', 'Higher Order\nThinking\n(C3-C6)']
        lots_hots_colors = ['#60a5fa', '#f97316']
        
        wedges, texts, autotexts = ax1.pie(
            lots_hots_data,
            labels=lots_hots_labels,
            colors=lots_hots_colors,
            autopct=lambda pct: f'{pct:.1f}%\n({int(pct*total_questions/100)})' if pct > 0 else '',
            startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=3, antialiased=True),
            explode=[0.05, 0.05],
            textprops={'fontsize': 10, 'fontweight': '600', 'color': '#374151'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax1.set_title('Cognitive Complexity', fontsize=13, fontweight='bold', 
                     color='#1e40af', pad=15)
        
        # Right: Category distribution - Elegant horizontal bars
        categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        category_names = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
        counts = [category_counts.get(cat, 0) for cat in categories]
        colors_hex = ['#10b981', '#3b82f6', '#f59e0b', '#f97316', '#ef4444', '#a855f7']
        
        y_pos = np.arange(len(categories))
        bars = ax2.barh(y_pos, counts, color=colors_hex, alpha=0.85, 
                       edgecolor='white', linewidth=2, height=0.7)
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([f'{cat}' for cat in categories], 
                           fontsize=11, fontweight='bold', color='#374151')
        ax2.set_xlabel('Number of Questions', fontsize=11, fontweight='bold', 
                      color='#374151', labelpad=8)
        ax2.set_title('Distribution by Level', fontsize=13, fontweight='bold', 
                     color='#1e40af', pad=15)
        
        # Style the axis
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#cbd5e1')
        ax2.spines['bottom'].set_color('#cbd5e1')
        ax2.tick_params(colors='#64748b', labelsize=10)
        
        # Add elegant grid
        ax2.xaxis.grid(True, linestyle='--', alpha=0.25, color='#cbd5e1', linewidth=1)
        ax2.set_axisbelow(True)
        
        # Add value labels with better positioning
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            percentage = (count / total_questions * 100) if total_questions > 0 else 0
            if width > 0:
                ax2.text(width + (max(counts) * 0.02), bar.get_y() + bar.get_height()/2.,
                        f' {count} ({percentage:.1f}%)',
                        ha='left', va='center', fontsize=9, fontweight='600',
                        color='#374151')
        
        plt.tight_layout()
        
        # Save to BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=180, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        logger.error(f"Error generating summary chart: {str(e)}", exc_info=True)
        return None


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
    """Generate and download PDF report with visualizations"""
    try:
        classification = get_object_or_404(
            ClassificationHistory, 
            pk=pk, 
            user=request.user
        )
        
        if classification.status != 'completed':
            messages.error(request, 'Classification not completed yet.')
            return redirect('klasifikasi:history')
        
        if not classification.classification_results:
            messages.error(request, 'No results available.')
            return redirect('klasifikasi:history')
        
        results = classification.classification_results
        questions_data = results.get('questions', [])
        category_counts = results.get('category_counts', {})
        
        # Generate charts
        bar_chart_buffer = generate_bar_chart(category_counts, classification.total_questions)
        doughnut_chart_buffer = generate_doughnut_chart(category_counts, classification.total_questions)
        summary_chart_buffer = generate_summary_chart(category_counts, classification.total_questions)
        
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
        
        # Info table
        info_data = [
            ['File Name:', classification.filename],
            ['Classification ID:', f"#{classification.id}"],
            ['Generated On:', timezone.now().strftime('%d/%m/%Y %H:%M')],
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # === VISUAL ANALYSIS SECTION ===
        elements.append(PageBreak())
        elements.append(Paragraph("Visual Analysis", heading_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Summary Chart (LOTS vs HOTS + Distribution) - Top of page
        if summary_chart_buffer:
            summary_img = Image(summary_chart_buffer, width=6.5*inch, height=2.925*inch)
            elements.append(summary_img)
            elements.append(Spacer(1, 0.25*inch))
        
        # Create a table layout for bar and doughnut charts side by side
        chart_row = []
        
        # Bar Chart
        if bar_chart_buffer:
            bar_img = Image(bar_chart_buffer, width=3.2*inch, height=1.76*inch)
            chart_row.append(bar_img)
        
        # Doughnut Chart
        if doughnut_chart_buffer:
            doughnut_img = Image(doughnut_chart_buffer, width=3.2*inch, height=1.76*inch)
            chart_row.append(doughnut_img)
        
        # Add charts in a table for side-by-side layout
        if chart_row:
            chart_table = Table([chart_row], colWidths=[3.2*inch, 3.2*inch])
            chart_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(chart_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # === DISTRIBUTION TABLE ===
        elements.append(PageBreak())
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
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(dist_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Statistical Summary
        elements.append(Paragraph("Statistical Summary", subheading_style))
        lots = category_counts.get('C1', 0) + category_counts.get('C2', 0)
        hots = sum(category_counts.get(f'C{i}', 0) for i in range(3, 7))
        
        stats_data = [
            ['Metric', 'Value'],
            ['Lower Order Thinking (C1-C2)', f"{lots} questions ({(lots/total*100):.1f}%)" if total > 0 else "0"],
            ['Higher Order Thinking (C3-C6)', f"{hots} questions ({(hots/total*100):.1f}%)" if total > 0 else "0"],
            ['Most Common Category', max(category_counts, key=category_counts.get) if category_counts else "N/A"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # === QUESTIONS SECTION ===
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
            
            # Escape HTML characters in question text
            question_text = question['question_text'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            q_text = Paragraph(question_text, normal_style)
            
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
        
        # === FOOTER ===
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
    """API endpoint for classification statistics"""
    try:
        classifications = ClassificationHistory.objects.filter(user=request.user)
        
        aggregates = classifications.aggregate(
            total=Count('id'),
            total_questions=Sum('total_questions'),
            completed=Count('id', filter=Q(status='completed')),
            processing=Count('id', filter=Q(status='processing')),
            failed=Count('id', filter=Q(status='failed')),
        )
        
        # Category totals
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
        logger.error(f"Error fetching stats: {str(e)}", exc_info=True)
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
        
        logger.info(f"Bulk deleted {deleted_count} classifications by {request.user.username}")
        
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
            'error': 'An error occurred'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def export_classification_excel(request, pk):
    """Export classification to Excel (CSV as fallback)"""
    try:
        classification = get_object_or_404(
            ClassificationHistory,
            pk=pk,
            user=request.user
        )
        
        if classification.status != 'completed':
            messages.error(request, 'Classification not completed yet.')
            return redirect('klasifikasi:hasil_klasifikasi', pk=pk)
        
        if not classification.classification_results:
            messages.error(request, 'No results available.')
            return redirect('klasifikasi:hasil_klasifikasi', pk=pk)
        
        # Export as CSV
        import csv
        from django.http import StreamingHttpResponse
        
        results = classification.classification_results
        questions = results.get('questions', [])
        
        response = HttpResponse(content_type='text/csv')
        filename = f"classification_{pk}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['No', 'Question', 'Category', 'Level Name', 'Confidence', 'Manually Modified'])
        
        for q in questions:
            writer.writerow([
                q['question_number'],
                q['question_text'],
                q['category'],
                q['category_name'],
                f"{q['confidence']*100:.1f}%",
                'Yes' if q.get('manually_modified', False) else 'No'
            ])
        
        logger.info(f"CSV export: {classification.filename} by {request.user.username}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}", exc_info=True)
        messages.error(request, 'Error exporting. Please try again.')
        return redirect('klasifikasi:hasil_klasifikasi', pk=pk)


@login_required
@require_http_methods(["GET"])
def get_question_details(request, classification_id, question_id):
    """API endpoint to get detailed info about a specific question"""
    try:
        classification = get_object_or_404(
            ClassificationHistory,
            pk=classification_id,
            user=request.user
        )
        
        if not classification.classification_results:
            return JsonResponse({
                'success': False,
                'error': 'No results found'
            }, status=404)
        
        questions = classification.classification_results.get('questions', [])
        
        # Find question by ID
        question = None
        for q in questions:
            if q.get('question_number') == int(question_id):
                question = q
                break
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question not found'
            }, status=404)
        
        data = {
            'id': question['question_number'],
            'number': question['question_number'],
            'text': question['question_text'],
            'category': question['category'],
            'category_name': question['category_name'],
            'confidence': question['confidence'],
            'formatted_confidence': f"{question['confidence']*100:.1f}%",
            'is_manually_classified': question.get('manually_modified', False),
            'was_adjusted': question.get('was_adjusted', False),
            'all_probabilities': question.get('all_probabilities', {})
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error fetching question details: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch question details'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def classification_analytics(request, pk):
    """Display detailed analytics for a classification"""
    try:
        classification = get_object_or_404(
            ClassificationHistory,
            pk=pk,
            user=request.user
        )
        
        if classification.status != 'completed':
            messages.info(request, 'Analytics available only for completed classifications.')
            return redirect('klasifikasi:hasil_klasifikasi', pk=pk)
        
        if not classification.classification_results:
            messages.error(request, 'No results available.')
            return redirect('klasifikasi:history')
        
        results = classification.classification_results
        questions = results.get('questions', [])
        category_counts = results.get('category_counts', {})
        
        # Calculate statistics
        total_questions = len(questions)
        
        # Confidence statistics
        confidences = [q['confidence'] for q in questions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        min_confidence = min(confidences) if confidences else 0
        max_confidence = max(confidences) if confidences else 0
        
        # Manual modifications count
        manual_count = sum(1 for q in questions if q.get('manually_modified', False))
        auto_count = total_questions - manual_count
        
        # Adjusted count
        adjusted_count = sum(1 for q in questions if q.get('was_adjusted', False))
        
        # Distribution percentages
        distribution = {}
        for cat, count in category_counts.items():
            distribution[cat] = {
                'count': count,
                'percentage': (count / total_questions * 100) if total_questions > 0 else 0
            }
        
        # Lower vs Higher order
        lower_order = category_counts.get('C1', 0) + category_counts.get('C2', 0)
        higher_order = sum(category_counts.get(f'C{i}', 0) for i in range(3, 7))
        
        context = {
            'classification': classification,
            'distribution': distribution,
            'avg_confidence': avg_confidence * 100,
            'min_confidence': min_confidence * 100,
            'max_confidence': max_confidence * 100,
            'manual_count': manual_count,
            'auto_count': auto_count,
            'adjusted_count': adjusted_count,
            'lower_order': lower_order,
            'higher_order': higher_order,
            'total_questions': total_questions,
            'category_counts': category_counts
        }
        
        return render(request, 'klasifikasi/analytics.html', context)
        
    except Exception as e:
        logger.error(f"Error loading analytics: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading analytics.')
        return redirect('klasifikasi:history')


@login_required
@require_http_methods(["POST"])
def reprocess_classification(request, pk):
    """Reprocess classification with ML model"""
    try:
        classification = get_object_or_404(
            ClassificationHistory,
            pk=pk,
            user=request.user
        )
        
        if not classification.file_path:
            return JsonResponse({
                'success': False,
                'error': 'Original file not found'
            }, status=404)
        
        # Mark as processing
        classification.mark_as_processing()
        
        # Trigger reprocessing
        from apps.soal.views import process_classification_sync
        process_classification_sync(classification.id)
        
        return JsonResponse({
            'success': True,
            'message': 'Classification reprocessed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error reprocessing: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to reprocess'
        }, status=500)