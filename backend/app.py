from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import DatabaseManager
from data_analyzer import DataAnalyzer

app = Flask(__name__)
CORS(app)  # 프론트엔드에서 접근 허용

# 데이터베이스 및 분석기 초기화
db = DatabaseManager()
analyzer = DataAnalyzer()

@app.route('/')
def home():
    """API 상태 확인"""
    return jsonify({
        'status': 'success',
        'message': '데이터 분석 모델 추천 시스템 API',
        'version': '1.0.0'
    })

@app.route('/api/analysis-steps', methods=['GET'])
def get_analysis_steps():
    """분석 단계 목록 조회"""
    try:
        steps = db.get_analysis_steps()
        return jsonify({
            'status': 'success',
            'data': steps
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """모델 카테고리 목록 조회"""
    try:
        categories = db.get_categories()
        return jsonify({
            'status': 'success',
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """모델 목록 조회"""
    try:
        category_id = request.args.get('category_id', type=int)
        models = db.get_models_by_category(category_id)
        return jsonify({
            'status': 'success',
            'data': models
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/recommend-models', methods=['POST'])
def recommend_models():
    """프로젝트 요구사항에 따른 모델 추천"""
    try:
        project_requirements = request.json
        
        # 필수 필드 검증
        required_fields = ['data_type', 'problem_type', 'dataset_size']
        for field in required_fields:
            if field not in project_requirements:
                return jsonify({
                    'status': 'error',
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        recommended_models = analyzer.recommend_models(project_requirements)
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommended_models': recommended_models,
                'total_count': len(recommended_models)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/step-recommendations/<int:step_order>', methods=['POST'])
def get_step_recommendations(step_order):
    """특정 단계의 추천 사항 조회"""
    try:
        project_data = request.json or {}
        recommendations = analyzer.get_step_recommendations(step_order, project_data)
        
        if not recommendations:
            return jsonify({
                'status': 'error',
                'message': '해당 단계를 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/model-guide/<int:model_id>', methods=['GET'])
def get_model_guide(model_id):
    """특정 모델의 구현 가이드 조회"""
    try:
        guide = analyzer.get_model_implementation_guide(model_id)
        
        if not guide:
            return jsonify({
                'status': 'error',
                'message': '해당 모델을 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': guide
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """분석 결과 리포트 생성"""
    try:
        project_data = request.json
        
        # 필수 필드 검증
        required_fields = ['project_name', 'data_type', 'problem_type']
        for field in required_fields:
            if field not in project_data:
                return jsonify({
                    'status': 'error',
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        report = analyzer.generate_analysis_report(project_data)
        
        return jsonify({
            'status': 'success',
            'data': report
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/save-project', methods=['POST'])
def save_project():
    """분석 프로젝트 저장"""
    try:
        project_data = request.json
        
        # 필수 필드 검증
        required_fields = ['project_name', 'data_type', 'problem_type']
        for field in required_fields:
            if field not in project_data:
                return jsonify({
                    'status': 'error',
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        project_id = db.save_project(project_data)
        
        return jsonify({
            'status': 'success',
            'data': {
                'project_id': project_id,
                'message': '프로젝트가 성공적으로 저장되었습니다.'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    try:
        # 데이터베이스 연결 테스트
        categories = db.get_categories()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'categories_count': len(categories)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 데이터 분석 모델 추천 시스템 서버 시작...")
    print("📊 API 문서: http://localhost:5000")
    print("💾 데이터베이스 초기화 중...")
    
    # 서버 시작
    app.run(host='0.0.0.0', port=5000, debug=True)