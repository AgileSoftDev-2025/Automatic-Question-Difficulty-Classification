// State management
let questions = [];
let currentCategory = 'C1';
let distributionChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadQuestions();
    setupEventListeners();
    renderQuestionNavigation();
    renderQuestions();
    updateOverview();
});

// Load questions from backend
async function loadQuestions() {
    try {
        const response = await fetch('/api/questions/');
        const data = await response.json();
        questions = data.questions || [];
    } catch (error) {
        console.error('Error loading questions:', error);
        // Fallback to demo data
        questions = generateDemoData();
    }
}

// Generate demo data for testing
function generateDemoData() {
    const demoQuestions = [
        {
            id: 1,
            text: 'Jelaskan secara singkat apa yang dimaksud dengan User Persona dalam proses desain interaksi.',
            classification: 'C1'
        },
        {
            id: 2,
            text: 'HealthBridge merancang sistem notifikasi untuk pasien. Berdasarkan hasil wawancara, user di daerah 3T lebih familiar menggunakan WhatsApp daripada notifikasi aplikasi. Terapkan konsep User-Centered Design untuk menjelaskan mengapa WhatsApp lebih efektif digunakan pada sistem HealthBridge dibandingkan notifikasi aplikasi bawaan.',
            classification: 'C3'
        },
        {
            id: 3,
            text: 'Dalam Feature Prioritization Matrix (MoSCoW), fitur Gamification untuk Donatur ditempatkan pada kategori Could Have. Menurut pendapatmu, apakah fitur ini sebaiknya tetap dipertahankan dalam roadmap pengembangan? Berikan alasan evaluatif berdasarkan kebutuhan user dan tujuan utama platform.',
            classification: 'C6'
        }
    ];
    
    // Generate more questions
    for (let i = 4; i <= 21; i++) {
        const categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'];
        demoQuestions.push({
            id: i,
            text: `Question ${i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`,
            classification: categories[Math.floor(Math.random() * categories.length)]
        });
    }
    
    return demoQuestions;
}

// Setup event listeners
function setupEventListeners() {
    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            currentCategory = e.target.dataset.category;
            
            // Update active tab
            document.querySelectorAll('.category-tab').forEach(t => {
                t.classList.remove('active', 'bg-white');
                t.classList.add('bg-gray-300');
            });
            e.target.classList.add('active', 'bg-white');
            e.target.classList.remove('bg-gray-300');
            
            renderQuestions();
        });
    });
    
    // View tabs
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const view = e.target.dataset.view;
            
            // Update active tab
            document.querySelectorAll('.view-tab').forEach(t => {
                t.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
                t.classList.add('text-gray-600');
            });
            e.target.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
            e.target.classList.remove('text-gray-600');
            
            // Toggle views
            if (view === 'detail') {
                document.getElementById('detailView').classList.remove('hidden');
                document.getElementById('overviewView').classList.add('hidden');
            } else {
                document.getElementById('detailView').classList.add('hidden');
                document.getElementById('overviewView').classList.remove('hidden');
                renderDistributionChart();
            }
        });
    });
    
    // Download button
    document.getElementById('downloadBtn').addEventListener('click', async () => {
        try {
            const response = await fetch('/api/download-pdf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'classified_questions.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert('Error downloading PDF. Please try again.');
        }
    });
}

// Render question navigation
function renderQuestionNavigation() {
    const nav = document.getElementById('questionNav');
    nav.innerHTML = '';
    
    questions.forEach((q, index) => {
        const btn = document.createElement('button');
        btn.className = 'aspect-square rounded font-semibold text-sm transition hover:scale-105';
        btn.textContent = q.id;
        btn.dataset.questionId = q.id;
        
        // Color based on classification
        const colors = {
            'C1': 'bg-blue-200 text-blue-800 border-2 border-blue-400',
            'C2': 'bg-green-200 text-green-800 border-2 border-green-400',
            'C3': 'bg-yellow-200 text-yellow-800 border-2 border-yellow-400',
            'C4': 'bg-orange-200 text-orange-800 border-2 border-orange-400',
            'C5': 'bg-purple-200 text-purple-800 border-2 border-purple-400',
            'C6': 'bg-pink-200 text-pink-800 border-2 border-pink-400'
        };
        
        btn.className += ' ' + (colors[q.classification] || 'bg-gray-200 text-gray-800');
        
        btn.addEventListener('click', () => {
            document.getElementById(`question-${q.id}`).scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        });
        
        nav.appendChild(btn);
    });
}

// Render questions for current category
function renderQuestions() {
    const container = document.getElementById('detailView');
    const filteredQuestions = questions.filter(q => q.classification === currentCategory);
    
    if (filteredQuestions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-500">
                <i class="bi bi-inbox text-6xl mb-4"></i>
                <p class="text-xl">No questions in ${currentCategory}</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredQuestions.map(q => `
        <div id="question-${q.id}" class="bg-white border-2 border-blue-100 rounded-lg p-6 shadow-sm hover:shadow-md transition">
            <div class="flex flex-col lg:flex-row gap-6">
                <div class="flex-1">
                    <h3 class="text-xl font-bold text-gray-800 mb-3">Question ${q.id}</h3>
                    <p class="text-gray-700 leading-relaxed">${q.text}</p>
                </div>
                <div class="lg:w-48 flex-shrink-0">
                    <div class="bg-blue-600 text-white rounded-lg p-4">
                        <div class="text-center">
                            <div class="text-3xl font-bold mb-2">${q.classification}</div>
                            <div class="text-sm mb-4 opacity-90">Change Classification To:</div>
                        </div>
                        <select class="classification-select w-full bg-white text-gray-800 rounded px-3 py-2 cursor-pointer" 
                                data-question-id="${q.id}">
                            <option value="">Select</option>
                            ${['C1', 'C2', 'C3', 'C4', 'C5', 'C6'].map(c => 
                                `<option value="${c}" ${c === q.classification ? 'selected' : ''}>${c}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Add change listeners
    document.querySelectorAll('.classification-select').forEach(select => {
        select.addEventListener('change', async (e) => {
            const questionId = parseInt(e.target.dataset.questionId);
            const newClassification = e.target.value;
            
            if (newClassification) {
                await updateClassification(questionId, newClassification);
            }
        });
    });
}

// Update question classification
async function updateClassification(questionId, newClassification) {
    try {
        const response = await fetch('/api/update-classification/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                question_id: questionId,
                classification: newClassification
            })
        });
        
        if (response.ok) {
            // Update local state
            const question = questions.find(q => q.id === questionId);
            if (question) {
                question.classification = newClassification;
            }
            
            // Re-render
            renderQuestionNavigation();
            renderQuestions();
            updateOverview();
            
            // Show success message
            showNotification('Classification updated successfully!', 'success');
        }
    } catch (error) {
        console.error('Error updating classification:', error);
        showNotification('Error updating classification', 'error');
    }
}

// Update overview statistics
function updateOverview() {
    const total = questions.length;
    const classified = questions.filter(q => q.classification).length;
    const unclassified = total - classified;
    
    document.getElementById('totalQuestions').textContent = total;
    document.getElementById('classifiedCount').textContent = classified;
    document.getElementById('unclassifiedCount').textContent = unclassified;
}

// Render distribution chart
function renderDistributionChart() {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    // Count questions per category
    const distribution = {
        C1: 0, C2: 0, C3: 0, C4: 0, C5: 0, C6: 0
    };
    
    questions.forEach(q => {
        if (distribution.hasOwnProperty(q.classification)) {
            distribution[q.classification]++;
        }
    });
    
    // Destroy existing chart
    if (distributionChart) {
        distributionChart.destroy();
    }
    
    // Create new chart
    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(distribution),
            datasets: [{
                label: 'Number of Questions',
                data: Object.values(distribution),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(234, 179, 8, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(236, 72, 153, 0.8)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(34, 197, 94)',
                    'rgb(234, 179, 8)',
                    'rgb(249, 115, 22)',
                    'rgb(168, 85, 247)',
                    'rgb(236, 72, 153)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Question Distribution by Bloom\'s Taxonomy Level',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Utility: Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 transform transition-all duration-300 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}