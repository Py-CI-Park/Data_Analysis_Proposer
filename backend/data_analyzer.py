import json
from models import DatabaseManager

class DataAnalyzer:
    def __init__(self):
        self.db = DatabaseManager()
    
    def recommend_models(self, project_requirements):
        """
        프로젝트 요구사항에 따라 적절한 모델들을 추천
        """
        data_type = project_requirements.get('data_type', '')
        problem_type = project_requirements.get('problem_type', '')
        dataset_size = project_requirements.get('dataset_size', '')
        complexity_preference = project_requirements.get('complexity_preference', 'Intermediate')
        
        all_models = self.db.get_models_by_category()
        recommended_models = []
        
        # 데이터 타입과 문제 유형에 따른 모델 필터링
        for model in all_models:
            score = 0
            reasons = []
            
            # 문제 유형별 점수 계산
            if problem_type == 'classification':
                if any(keyword in model['use_cases'].lower() for keyword in ['분류', '진단', '예측', 'classification']):
                    score += 3
                    reasons.append("분류 문제에 적합")
            
            elif problem_type == 'regression':
                if any(keyword in model['use_cases'].lower() for keyword in ['예측', '가격', '매출', 'regression']):
                    score += 3
                    reasons.append("회귀 문제에 적합")
            
            elif problem_type == 'clustering':
                if any(keyword in model['use_cases'].lower() for keyword in ['세분화', '그룹', 'clustering']):
                    score += 3
                    reasons.append("클러스터링 문제에 적합")
            
            elif problem_type == 'time_series':
                if any(keyword in model['model_name'].lower() for keyword in ['lstm', 'arima', 'time']):
                    score += 3
                    reasons.append("시계열 분석에 적합")
            
            # 데이터 타입별 점수 계산
            if data_type == 'image' and 'image' in model['data_requirements'].lower():
                score += 2
                reasons.append("이미지 데이터 처리 가능")
            elif data_type == 'image' and model['model_name'].lower() in ['cnn', 'convolutional']:
                score += 3
                reasons.append("이미지 처리 특화 모델")
            
            if data_type == 'text' and any(keyword in model['use_cases'].lower() for keyword in ['번역', '텍스트', '자연어']):
                score += 2
                reasons.append("텍스트 데이터 처리 가능")
            
            if data_type == 'numerical' and model['model_type'] == 'ML':
                score += 1
                reasons.append("수치형 데이터에 효과적")
            
            # 데이터셋 크기별 점수 계산
            if dataset_size == 'small':
                if model['complexity_level'] in ['Beginner', 'Intermediate']:
                    score += 1
                    reasons.append("소규모 데이터에 적합")
                if model['model_type'] == 'DL':
                    score -= 1  # 딥러닝은 소규모 데이터에 불리
            
            elif dataset_size == 'large':
                if model['model_type'] == 'DL':
                    score += 2
                    reasons.append("대용량 데이터 처리 가능")
                if 'xgboost' in model['model_name'].lower():
                    score += 1
                    reasons.append("대용량 데이터에 효율적")
            
            # 복잡도 선호도 반영
            if complexity_preference == model['complexity_level']:
                score += 1
                reasons.append(f"{complexity_preference} 수준에 적합")
            
            # 점수가 있는 모델만 추천
            if score > 0:
                model_info = model.copy()
                model_info['recommendation_score'] = score
                model_info['recommendation_reasons'] = reasons
                recommended_models.append(model_info)
        
        # 점수 순으로 정렬하여 상위 5개 반환
        recommended_models.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommended_models[:5]
    
    def get_step_recommendations(self, current_step, project_data):
        """
        현재 단계에 따른 추천 사항 제공
        """
        steps = self.db.get_analysis_steps()
        current_step_info = next((step for step in steps if step['step_order'] == current_step), None)
        
        if not current_step_info:
            return None
        
        recommendations = {
            'current_step': current_step_info,
            'tips': [],
            'tools': [],
            'next_step': None
        }
        
        # 단계별 추천 사항
        if current_step == 1:  # 데이터 수집
            recommendations['tips'] = [
                "분석 목표를 명확히 정의하세요",
                "데이터 품질을 사전에 확인하세요",
                "충분한 양의 데이터를 확보하세요"
            ]
            recommendations['tools'] = ["pandas", "requests", "sqlalchemy"]
        
        elif current_step == 2:  # 데이터 전처리
            recommendations['tips'] = [
                "결측치 패턴을 분석하세요",
                "이상치를 탐지하고 처리하세요",
                "데이터 타입을 적절히 변환하세요"
            ]
            recommendations['tools'] = ["pandas", "numpy", "sklearn.preprocessing"]
        
        elif current_step == 3:  # EDA
            recommendations['tips'] = [
                "데이터 분포를 시각화하세요",
                "변수 간 상관관계를 분석하세요",
                "타겟 변수와 특성들의 관계를 파악하세요"
            ]
            recommendations['tools'] = ["matplotlib", "seaborn", "plotly"]
        
        elif current_step == 4:  # 특성 엔지니어링
            recommendations['tips'] = [
                "도메인 지식을 활용한 특성을 생성하세요",
                "특성의 중요도를 평가하세요",
                "차원의 저주를 피하기 위해 특성 선택을 수행하세요"
            ]
            recommendations['tools'] = ["sklearn.feature_selection", "pandas", "numpy"]
        
        elif current_step == 5:  # 모델 선택
            recommendations['tips'] = [
                "문제 유형에 적합한 모델을 선택하세요",
                "베이스라인 모델부터 시작하세요",
                "여러 모델을 비교 평가하세요"
            ]
            recommendations['tools'] = ["sklearn", "xgboost", "tensorflow"]
        
        # 다음 단계 정보
        if current_step < len(steps):
            next_step_info = next((step for step in steps if step['step_order'] == current_step + 1), None)
            recommendations['next_step'] = next_step_info
        
        return recommendations
    
    def generate_analysis_report(self, project_data):
        """
        분석 결과 리포트 생성
        """
        report = {
            'project_summary': {
                'name': project_data.get('project_name', ''),
                'data_type': project_data.get('data_type', ''),
                'problem_type': project_data.get('problem_type', ''),
                'dataset_size': project_data.get('dataset_size', '')
            },
            'selected_steps': project_data.get('selected_steps', []),
            'recommended_models': project_data.get('recommended_models', []),
            'key_insights': [],
            'recommendations': []
        }
        
        # 프로젝트 유형별 핵심 인사이트 생성
        if project_data.get('problem_type') == 'classification':
            report['key_insights'].append("분류 문제는 정확도, 정밀도, 재현율을 균형있게 고려해야 합니다.")
            report['recommendations'].append("교차검증을 통해 모델의 일반화 성능을 확인하세요.")
        
        elif project_data.get('problem_type') == 'regression':
            report['key_insights'].append("회귀 문제는 잔차 분석을 통해 모델의 가정을 검증해야 합니다.")
            report['recommendations'].append("특성과 타겟 변수의 선형성을 확인하세요.")
        
        # 데이터 크기별 권장사항
        if project_data.get('dataset_size') == 'small':
            report['recommendations'].append("작은 데이터셋에서는 과적합을 주의하고 정규화를 고려하세요.")
        elif project_data.get('dataset_size') == 'large':
            report['recommendations'].append("큰 데이터셋에서는 샘플링과 분산 처리를 고려하세요.")
        
        return report
    
    def get_model_implementation_guide(self, model_id):
        """
        특정 모델의 구현 가이드 제공
        """
        models = self.db.get_models_by_category()
        model = next((m for m in models if m['id'] == model_id), None)
        
        if not model:
            return None
        
        guide = {
            'model_info': model,
            'implementation_steps': [],
            'code_example': model['implementation_code'],
            'hyperparameters': json.loads(model['parameters']),
            'evaluation_metrics': model['performance_metrics'].split(', '),
            'best_practices': []
        }
        
        # 모델 타입별 구현 단계
        if model['model_type'] == 'ML':
            guide['implementation_steps'] = [
                "데이터 전처리 및 특성 스케일링",
                "훈련/검증/테스트 데이터 분할",
                "모델 초기화 및 하이퍼파라미터 설정",
                "모델 훈련",
                "성능 평가 및 검증",
                "결과 해석 및 시각화"
            ]
        elif model['model_type'] == 'DL':
            guide['implementation_steps'] = [
                "데이터 전처리 및 정규화",
                "모델 아키텍처 설계",
                "손실 함수 및 옵티마이저 선택",
                "훈련 루프 구현",
                "검증 및 조기 종료 설정",
                "모델 평가 및 시각화"
            ]
        elif model['model_type'] == 'RL':
            guide['implementation_steps'] = [
                "환경 설정 및 상태/행동 공간 정의",
                "보상 함수 설계",
                "에이전트 초기화",
                "탐험-활용 전략 설정",
                "훈련 루프 실행",
                "성능 모니터링 및 평가"
            ]
        
        # 모델별 모범 사례
        if 'forest' in model['model_name'].lower():
            guide['best_practices'] = [
                "특성 중요도를 활용한 특성 선택",
                "Out-of-bag 오차를 활용한 성능 추정",
                "트리 개수와 깊이의 균형 조절"
            ]
        elif 'neural' in model['model_name'].lower() or model['model_type'] == 'DL':
            guide['best_practices'] = [
                "배치 정규화로 훈련 안정성 향상",
                "드롭아웃으로 과적합 방지",
                "학습률 스케줄링 적용",
                "조기 종료로 최적 모델 저장"
            ]
        
        return guide