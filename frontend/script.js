// API 기본 URL
const API_BASE_URL = 'http://localhost:5000';

// 전역 변수
let currentProject = {};
let allModels = [];
let allCategories = [];
let allSteps = [];

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// 앱 초기화
async function initializeApp() {
    try {
        showLoader();
        await Promise.all([
            loadAnalysisSteps(),
            loadCategories(),
            loadModels()
        ]);
        hideLoader();
    } catch (error) {
        hideLoader();
        showNotification('초기화 중 오류가 발생했습니다: ' + error.message, 'error');
    }
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 네비게이션
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showSection(section);
        });
    });

    // 추천 폼 제출
    const recommendForm = document.getElementById('recommendForm');
    recommendForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleRecommendSubmit();
    });

    // 모델 필터
    document.getElementById('categoryFilter').addEventListener('change', filterModels);
    document.getElementById('typeFilter').addEventListener('change', filterModels);
    document.getElementById('complexityFilter').addEventListener('change', filterModels);

    // 모달 클릭 외부 닫기
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// API 호출 함수들
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'API 요청 실패');
        }

        return result;
    } catch (error) {
        console.error('API 호출 오류:', error);
        throw error;
    }
}

// 분석 단계 로드
async function loadAnalysisSteps() {
    try {
        const response = await apiCall('/api/analysis-steps');
        allSteps = response.data;
        renderAnalysisSteps();
    } catch (error) {
        console.error('분석 단계 로드 실패:', error);
    }
}

// 카테고리 로드
async function loadCategories() {
    try {
        const response = await apiCall('/api/categories');
        allCategories = response.data;
        renderCategoryFilter();
    } catch (error) {
        console.error('카테고리 로드 실패:', error);
    }
}

// 모델 로드
async function loadModels() {
    try {
        const response = await apiCall('/api/models');
        allModels = response.data;
        renderModels(allModels);
    } catch (error) {
        console.error('모델 로드 실패:', error);
    }
}

// 분석 단계 렌더링
function renderAnalysisSteps() {
    const timeline = document.getElementById('stepsTimeline');
    timeline.innerHTML = '';

    allSteps.forEach(step => {
        const stepElement = document.createElement('div');
        stepElement.className = 'step-item';
        stepElement.addEventListener('click', () => showStepDetails(step));
        
        stepElement.innerHTML = `
            <div class="step-number">단계 ${step.step_order}</div>
            <div class="step-name">${step.step_name}</div>
            <div class="step-description">${step.description}</div>
        `;
        
        timeline.appendChild(stepElement);
    });
}

// 단계 상세 정보 표시
async function showStepDetails(step) {
    // 활성 단계 표시
    document.querySelectorAll('.step-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.step-item').classList.add('active');

    const detailsContainer = document.getElementById('stepDetails');
    
    detailsContainer.innerHTML = `
        <h3>${step.step_name}</h3>
        <p>${step.description}</p>
        <div class="step-info">
            <div class="info-item">
                <div class="info-label">목적</div>
                <div>${step.purpose}</div>
            </div>
            <div class="info-item">
                <div class="info-label">예상 결과</div>
                <div>${step.expected_outcome}</div>
            </div>
            <div class="info-item">
                <div class="info-label">전제 조건</div>
                <div>${step.prerequisites}</div>
            </div>
        </div>
    `;

    // 단계별 추천 사항 로드
    try {
        const response = await apiCall(`/api/step-recommendations/${step.step_order}`, 'POST', currentProject);
        const recommendations = response.data;
        
        if (recommendations.tips && recommendations.tips.length > 0) {
            detailsContainer.innerHTML += `
                <div class="info-item">
                    <div class="info-label">추천 사항</div>
                    <ul>
                        ${recommendations.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (recommendations.tools && recommendations.tools.length > 0) {
            detailsContainer.innerHTML += `
                <div class="info-item">
                    <div class="info-label">추천 도구</div>
                    <div>${recommendations.tools.join(', ')}</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('단계 추천 사항 로드 실패:', error);
    }
}

// 카테고리 필터 렌더링
function renderCategoryFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    
    allCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.category_name;
        categoryFilter.appendChild(option);
    });
}

// 모델 렌더링
function renderModels(models) {
    const modelsGrid = document.getElementById('modelsGrid');
    modelsGrid.innerHTML = '';

    models.forEach(model => {
        const modelCard = document.createElement('div');
        modelCard.className = 'model-card';
        modelCard.addEventListener('click', () => showModelDetails(model));
        
        modelCard.innerHTML = `
            <div class="model-header">
                <div class="model-name">${model.model_name}</div>
                <div class="model-type ${model.model_type}">${model.model_type}</div>
            </div>
            <div class="model-description">${model.description}</div>
            <div class="model-complexity ${model.complexity_level}">
                ${getComplexityLabel(model.complexity_level)}
            </div>
        `;
        
        modelsGrid.appendChild(modelCard);
    });
}

// 복잡도 라벨 변환
function getComplexityLabel(complexity) {
    const labels = {
        'Beginner': '초급',
        'Intermediate': '중급',
        'Advanced': '고급'
    };
    return labels[complexity] || complexity;
}

// 모델 필터링
function filterModels() {
    const categoryFilter = document.getElementById('categoryFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    const complexityFilter = document.getElementById('complexityFilter').value;

    let filteredModels = allModels.filter(model => {
        if (categoryFilter && model.category_id !== parseInt(categoryFilter)) return false;
        if (typeFilter && model.model_type !== typeFilter) return false;
        if (complexityFilter && model.complexity_level !== complexityFilter) return false;
        return true;
    });

    renderModels(filteredModels);
}

// 모델 상세 정보 표시
async function showModelDetails(model) {
    try {
        showLoader();
        const response = await apiCall(`/api/model-guide/${model.id}`);
        const guide = response.data;
        hideLoader();

        document.getElementById('modalModelName').textContent = model.model_name;
        document.getElementById('modalModelContent').innerHTML = `
            <div class="model-detail">
                <div class="detail-section">
                    <h4>모델 설명</h4>
                    <p>${model.description}</p>
                </div>
                
                <div class="detail-section">
                    <h4>사용 사례</h4>
                    <p>${model.use_cases}</p>
                </div>
                
                <div class="detail-section">
                    <h4>장점</h4>
                    <p>${model.advantages}</p>
                </div>
                
                <div class="detail-section">
                    <h4>단점</h4>
                    <p>${model.disadvantages}</p>
                </div>
                
                <div class="detail-section">
                    <h4>데이터 요구사항</h4>
                    <p>${model.data_requirements}</p>
                </div>
                
                <div class="detail-section">
                    <h4>성능 지표</h4>
                    <p>${model.performance_metrics}</p>
                </div>
                
                <div class="detail-section">
                    <h4>구현 예제</h4>
                    <div class="code-block">${model.implementation_code}</div>
                </div>
                
                ${guide.implementation_steps ? `
                    <div class="detail-section">
                        <h4>구현 단계</h4>
                        <ol>
                            ${guide.implementation_steps.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                    </div>
                ` : ''}
                
                ${guide.best_practices && guide.best_practices.length > 0 ? `
                    <div class="detail-section">
                        <h4>모범 사례</h4>
                        <ul>
                            ${guide.best_practices.map(practice => `<li>${practice}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;

        document.getElementById('modelModal').style.display = 'block';
    } catch (error) {
        hideLoader();
        showNotification('모델 상세 정보를 불러오는데 실패했습니다: ' + error.message, 'error');
    }
}

// 추천 폼 제출 처리
async function handleRecommendSubmit() {
    try {
        showLoader();
        
        const formData = new FormData(document.getElementById('recommendForm'));
        const projectData = {};
        for (let [key, value] of formData.entries()) {
            projectData[key] = value;
        }
        
        currentProject = projectData;
        
        const response = await apiCall('/api/recommend-models', 'POST', projectData);
        const recommendedModels = response.data.recommended_models;
        
        renderRecommendedModels(recommendedModels);
        document.getElementById('recommendResults').classList.remove('hidden');
        
        hideLoader();
        showNotification('모델 추천이 완료되었습니다!', 'success');
        
    } catch (error) {
        hideLoader();
        showNotification('모델 추천 중 오류가 발생했습니다: ' + error.message, 'error');
    }
}

// 추천 모델 렌더링
function renderRecommendedModels(models) {
    const container = document.getElementById('recommendedModels');
    container.innerHTML = '';

    models.forEach((model, index) => {
        const modelElement = document.createElement('div');
        modelElement.className = 'recommended-model';
        
        const stars = '★'.repeat(Math.min(5, model.recommendation_score));
        
        modelElement.innerHTML = `
            <div class="recommendation-rank">#${index + 1}</div>
            <div class="model-header">
                <div class="model-name">${model.model_name}</div>
                <div class="model-type ${model.model_type}">${model.model_type}</div>
            </div>
            <div class="recommendation-score">
                <span class="score-stars">${stars}</span>
                <span>추천 점수: ${model.recommendation_score}</span>
            </div>
            <div class="model-description">${model.description}</div>
            <div class="recommendation-reasons">
                <strong>추천 이유:</strong>
                <div>
                    ${model.recommendation_reasons.map(reason => 
                        `<span class="reason-tag">${reason}</span>`
                    ).join('')}
                </div>
            </div>
            <button class="btn btn-primary" onclick="showModelDetails(${JSON.stringify(model).replace(/"/g, '&quot;')})">
                <i class="fas fa-info-circle"></i>
                상세 정보
            </button>
        `;
        
        container.appendChild(modelElement);
    });
    
    // 추천 모델을 currentProject에 저장
    currentProject.recommended_models = models;
}

// 리포트 생성
async function generateReport() {
    try {
        if (!currentProject.project_name) {
            showNotification('먼저 모델 추천을 받아주세요.', 'warning');
            return;
        }
        
        showLoader();
        
        const response = await apiCall('/api/generate-report', 'POST', currentProject);
        const report = response.data;
        
        renderReport(report);
        document.getElementById('reportModal').style.display = 'block';
        
        hideLoader();
        
    } catch (error) {
        hideLoader();
        showNotification('리포트 생성 중 오류가 발생했습니다: ' + error.message, 'error');
    }
}

// 리포트 렌더링
function renderReport(report) {
    const container = document.getElementById('reportContent');
    
    container.innerHTML = `
        <div class="report">
            <div class="detail-section">
                <h4>프로젝트 요약</h4>
                <p><strong>프로젝트명:</strong> ${report.project_summary.name}</p>
                <p><strong>데이터 타입:</strong> ${report.project_summary.data_type}</p>
                <p><strong>문제 유형:</strong> ${report.project_summary.problem_type}</p>
                <p><strong>데이터셋 크기:</strong> ${report.project_summary.dataset_size}</p>
            </div>
            
            ${report.key_insights && report.key_insights.length > 0 ? `
                <div class="detail-section">
                    <h4>핵심 인사이트</h4>
                    <ul>
                        ${report.key_insights.map(insight => `<li>${insight}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${report.recommendations && report.recommendations.length > 0 ? `
                <div class="detail-section">
                    <h4>권장 사항</h4>
                    <ul>
                        ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${report.recommended_models && report.recommended_models.length > 0 ? `
                <div class="detail-section">
                    <h4>추천 모델 요약</h4>
                    <ol>
                        ${report.recommended_models.map(model => `
                            <li>
                                <strong>${model.model_name}</strong> (${model.model_type})
                                <br>추천 점수: ${model.recommendation_score}
                            </li>
                        `).join('')}
                    </ol>
                </div>
            ` : ''}
        </div>
    `;
}

// 프로젝트 저장
async function saveProject() {
    try {
        if (!currentProject.project_name) {
            showNotification('먼저 모델 추천을 받아주세요.', 'warning');
            return;
        }
        
        showLoader();
        
        const response = await apiCall('/api/save-project', 'POST', currentProject);
        
        hideLoader();
        showNotification('프로젝트가 성공적으로 저장되었습니다!', 'success');
        
    } catch (error) {
        hideLoader();
        showNotification('프로젝트 저장 중 오류가 발생했습니다: ' + error.message, 'error');
    }
}

// 섹션 표시
function showSection(sectionId) {
    // 모든 섹션 숨기기
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // 모든 네비게이션 링크 비활성화
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // 선택된 섹션 표시
    document.getElementById(sectionId).classList.add('active');
    
    // 해당 네비게이션 링크 활성화
    document.querySelector(`[href="#${sectionId}"]`).classList.add('active');
}

// 모달 닫기
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// 로더 표시/숨기기
function showLoader() {
    document.getElementById('loader').classList.remove('hidden');
}

function hideLoader() {
    document.getElementById('loader').classList.add('hidden');
}

// 알림 표시
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const messageElement = document.getElementById('notificationMessage');
    
    messageElement.textContent = message;
    
    // 타입에 따른 스타일 적용
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    // 5초 후 자동 숨김
    setTimeout(() => {
        hideNotification();
    }, 5000);
}

function hideNotification() {
    document.getElementById('notification').classList.add('hidden');
}