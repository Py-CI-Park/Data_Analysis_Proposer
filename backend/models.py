import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 분석 단계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_name TEXT NOT NULL,
                step_order INTEGER NOT NULL,
                description TEXT,
                purpose TEXT,
                expected_outcome TEXT,
                prerequisites TEXT
            )
        ''')
        
        # 모델 카테고리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')
        
        # 머신러닝/딥러닝/강화학습 모델 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                category_id INTEGER,
                model_type TEXT NOT NULL, -- ML, DL, RL
                description TEXT,
                use_cases TEXT,
                advantages TEXT,
                disadvantages TEXT,
                complexity_level TEXT, -- Beginner, Intermediate, Advanced
                data_requirements TEXT,
                performance_metrics TEXT,
                implementation_code TEXT,
                parameters TEXT, -- JSON format
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES model_categories (id)
            )
        ''')
        
        # 데이터 분석 프로젝트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                data_type TEXT,
                problem_type TEXT,
                dataset_size TEXT,
                selected_steps TEXT, -- JSON format
                recommended_models TEXT, -- JSON format
                results TEXT, -- JSON format
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 초기 데이터 삽입
        self.populate_initial_data()
    
    def populate_initial_data(self):
        """초기 데이터 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 분석 단계 데이터
        analysis_steps = [
            (1, "데이터 수집", "분석에 필요한 데이터를 수집하고 불러오는 단계", 
             "분석 목적에 맞는 양질의 데이터 확보", "구조화된 데이터셋 준비", "분석 목표 설정"),
            (2, "데이터 전처리", "수집된 데이터를 분석에 적합하게 가공하는 단계",
             "데이터 품질 향상 및 분석 준비", "깨끗하고 일관된 데이터", "원시 데이터"),
            (3, "탐색적 데이터 분석(EDA)", "데이터의 특성과 패턴을 파악하는 단계",
             "데이터 이해 및 인사이트 발견", "데이터 특성 요약 및 시각화", "전처리된 데이터"),
            (4, "특성 엔지니어링", "모델 성능 향상을 위한 특성 추출 및 변환",
             "예측력 높은 특성 생성", "최적화된 특성 세트", "EDA 결과"),
            (5, "모델 선택", "문제에 적합한 머신러닝 모델 선택",
             "최적의 알고리즘 선택", "성능 좋은 모델 후보군", "준비된 특성"),
            (6, "모델 훈련", "선택된 모델을 데이터로 학습시키는 단계",
             "모델 파라미터 최적화", "훈련된 모델", "선택된 모델과 데이터"),
            (7, "모델 평가", "모델의 성능을 평가하고 검증하는 단계",
             "모델 성능 측정 및 검증", "성능 지표 및 평가 결과", "훈련된 모델"),
            (8, "결과 해석", "모델 결과를 분석하고 비즈니스 인사이트 도출",
             "실무진이 이해할 수 있는 인사이트 제공", "의사결정을 위한 결과 리포트", "평가된 모델")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO analysis_steps 
            (step_order, step_name, description, purpose, expected_outcome, prerequisites)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', analysis_steps)
        
        # 모델 카테고리 데이터
        categories = [
            ("회귀 분석", "연속적인 수치값을 예측하는 모델들"),
            ("분류", "카테고리나 클래스를 예측하는 모델들"),
            ("클러스터링", "데이터를 그룹으로 나누는 비지도 학습 모델들"),
            ("차원 축소", "데이터의 차원을 줄이는 모델들"),
            ("딥러닝", "신경망 기반의 복잡한 모델들"),
            ("강화학습", "환경과의 상호작용을 통해 학습하는 모델들"),
            ("시계열 분석", "시간에 따른 데이터 패턴을 분석하는 모델들"),
            ("자연어 처리", "텍스트 데이터를 처리하는 모델들"),
            ("컴퓨터 비전", "이미지 데이터를 처리하는 모델들")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO model_categories (category_name, description)
            VALUES (?, ?)
        ''', categories)
        
        # ML/DL/RL 모델 데이터
        models = [
            # 머신러닝 모델들
            ("Linear Regression", 1, "ML", 
             "선형 관계를 가정한 회귀 모델", 
             "주택 가격 예측, 매출 예측, 연속값 예측",
             "해석이 쉽고 계산이 빠름", "비선형 관계 포착 어려움",
             "Beginner", "연속형 타겟, 수치형 특성", "MSE, MAE, R²",
             "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()",
             '{"fit_intercept": true, "normalize": false}'),
            
            ("Random Forest", 2, "ML",
             "다수의 결정 트리를 결합한 앙상블 모델",
             "고객 세분화, 질병 진단, 이미지 분류",
             "과적합 방지, 특성 중요도 제공", "해석이 어려움",
             "Intermediate", "범주형/수치형 혼합 데이터", "Accuracy, Precision, Recall",
             "from sklearn.ensemble import RandomForestClassifier\nmodel = RandomForestClassifier()",
             '{"n_estimators": 100, "max_depth": null}'),
            
            ("XGBoost", 2, "ML",
             "그래디언트 부스팅 기반의 고성능 앙상블 모델",
             "경진대회, 금융 예측, 추천 시스템",
             "높은 성능, 결측치 처리", "하이퍼파라미터 튜닝 복잡",
             "Advanced", "대용량 데이터", "AUC, F1-Score",
             "import xgboost as xgb\nmodel = xgb.XGBClassifier()",
             '{"learning_rate": 0.1, "max_depth": 6}'),
            
            ("K-Means", 3, "ML",
             "거리 기반 클러스터링 알고리즘",
             "고객 세분화, 시장 세분화, 이미지 분할",
             "간단하고 빠름", "클러스터 수 사전 지정 필요",
             "Beginner", "수치형 데이터", "Silhouette Score, Inertia",
             "from sklearn.cluster import KMeans\nmodel = KMeans()",
             '{"n_clusters": 3, "random_state": 42}'),
            
            # 딥러닝 모델들
            ("Convolutional Neural Network", 9, "DL",
             "이미지 처리에 특화된 딥러닝 모델",
             "이미지 분류, 객체 탐지, 의료 영상 분석",
             "이미지 특성 자동 추출", "대용량 데이터 필요",
             "Advanced", "이미지 데이터", "Accuracy, Top-5 Accuracy",
             "import tensorflow as tf\nmodel = tf.keras.Sequential([tf.keras.layers.Conv2D()])",
             '{"filters": 32, "kernel_size": 3}'),
            
            ("LSTM", 7, "DL",
             "순환 신경망의 한 종류로 시계열 데이터 처리",
             "주가 예측, 자연어 처리, 음성 인식",
             "장기 의존성 학습 가능", "훈련 시간 오래 걸림",
             "Advanced", "시계열 데이터", "RMSE, MAPE",
             "from tensorflow.keras.layers import LSTM\nmodel = Sequential([LSTM(50)])",
             '{"units": 50, "return_sequences": false}'),
            
            ("Transformer", 8, "DL",
             "어텐션 메커니즘 기반의 딥러닝 모델",
             "기계 번역, 텍스트 요약, 질의응답",
             "병렬 처리 가능, 높은 성능", "메모리 사용량 많음",
             "Advanced", "텍스트 데이터", "BLEU, ROUGE",
             "from transformers import AutoModel\nmodel = AutoModel.from_pretrained('bert-base-uncased')",
             '{"num_attention_heads": 12, "hidden_size": 768}'),
            
            # 강화학습 모델들
            ("Q-Learning", 6, "RL",
             "가치 기반 강화학습 알고리즘",
             "게임 AI, 로봇 제어, 자율주행",
             "모델 없이 학습 가능", "상태 공간이 클 때 비효율적",
             "Intermediate", "이산적 상태/행동 공간", "Average Reward, Success Rate",
             "import numpy as np\nQ = np.zeros((state_size, action_size))",
             '{"learning_rate": 0.1, "discount_factor": 0.95}'),
            
            ("Deep Q-Network (DQN)", 6, "RL",
             "딥러닝과 Q-Learning을 결합한 알고리즘",
             "비디오 게임, 로봇 제어, 추천 시스템",
             "연속 상태 공간 처리 가능", "샘플 효율성 낮음",
             "Advanced", "연속적 상태 공간", "Episode Reward, Q-Value",
             "import tensorflow as tf\nmodel = tf.keras.Sequential([tf.keras.layers.Dense(128)])",
             '{"memory_size": 10000, "batch_size": 32}')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO ml_models 
            (model_name, category_id, model_type, description, use_cases, 
             advantages, disadvantages, complexity_level, data_requirements, 
             performance_metrics, implementation_code, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', models)
        
        conn.commit()
        conn.close()
    
    def get_analysis_steps(self):
        """분석 단계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_steps ORDER BY step_order
        ''')
        
        steps = []
        for row in cursor.fetchall():
            steps.append({
                'id': row[0],
                'step_name': row[1],
                'step_order': row[2],
                'description': row[3],
                'purpose': row[4],
                'expected_outcome': row[5],
                'prerequisites': row[6]
            })
        
        conn.close()
        return steps
    
    def get_models_by_category(self, category_id=None):
        """카테고리별 모델 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category_id:
            cursor.execute('''
                SELECT m.*, c.category_name 
                FROM ml_models m 
                JOIN model_categories c ON m.category_id = c.id 
                WHERE m.category_id = ?
            ''', (category_id,))
        else:
            cursor.execute('''
                SELECT m.*, c.category_name 
                FROM ml_models m 
                JOIN model_categories c ON m.category_id = c.id
            ''')
        
        models = []
        for row in cursor.fetchall():
            models.append({
                'id': row[0],
                'model_name': row[1],
                'category_id': row[2],
                'model_type': row[3],
                'description': row[4],
                'use_cases': row[5],
                'advantages': row[6],
                'disadvantages': row[7],
                'complexity_level': row[8],
                'data_requirements': row[9],
                'performance_metrics': row[10],
                'implementation_code': row[11],
                'parameters': row[12],
                'created_at': row[13],
                'category_name': row[14]
            })
        
        conn.close()
        return models
    
    def get_categories(self):
        """모든 카테고리 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM model_categories')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'category_name': row[1],
                'description': row[2]
            })
        
        conn.close()
        return categories
    
    def save_project(self, project_data):
        """분석 프로젝트 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_projects 
            (project_name, data_type, problem_type, dataset_size, 
             selected_steps, recommended_models, results)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_data['project_name'],
            project_data['data_type'],
            project_data['problem_type'],
            project_data['dataset_size'],
            json.dumps(project_data['selected_steps']),
            json.dumps(project_data['recommended_models']),
            json.dumps(project_data['results'])
        ))
        
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        
        return project_id