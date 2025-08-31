"""
Treinador de Modelos de IA para Otimização
Treina modelos de machine learning para otimizar scores de priorização
"""

import asyncio
import json
import pickle
import sqlite3
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

from .data_collector import FeatureSet, TrainingData


@dataclass
class ModelMetrics:
    """Métricas de performance do modelo"""
    model_name: str
    r2_score: float
    mse: float
    mae: float
    cross_val_score: float
    training_time: float
    created_at: datetime


@dataclass
class TrainingResult:
    """Resultado do treinamento"""
    model_name: str
    model_path: str
    metrics: ModelMetrics
    feature_importance: Dict[str, float]
    training_data_size: int
    created_at: datetime


class ModelTrainer:
    """Treinador de modelos de IA"""
    
    def __init__(self, models_path: str = "models/ai_optimization"):
        self.models_path = Path(models_path)
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Modelos disponíveis
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        # Scaler para normalização
        self.scaler = StandardScaler()
        
        # Encoders para variáveis categóricas
        self.label_encoders = {}
        
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados para métricas"""
        try:
            db_path = self.models_path / "training_metrics.db"
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        r2_score REAL NOT NULL,
                        mse REAL NOT NULL,
                        mae REAL NOT NULL,
                        cross_val_score REAL NOT NULL,
                        training_time REAL NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS feature_importance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        feature_name TEXT NOT NULL,
                        importance REAL NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Banco de métricas inicializado")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de métricas: {e}")
    
    def _prepare_features(self, features: List[FeatureSet]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara features para treinamento"""
        try:
            # Extrair features numéricas
            numerical_features = []
            categorical_features = []
            
            for feature in features:
                numerical = [
                    feature.price,
                    feature.geek_score,
                    feature.conversion_rate,
                    feature.click_rate,
                    feature.engagement_rate,
                    feature.time_of_day,
                    feature.day_of_week,
                    feature.category_popularity,
                    feature.store_reputation,
                    feature.title_length,
                    float(feature.has_discount),
                    feature.discount_percentage
                ]
                
                categorical = [
                    feature.season,
                    feature.price_range,
                    feature.category,
                    feature.store
                ]
                
                numerical_features.append(numerical)
                categorical_features.append(categorical)
            
            # Converter para arrays
            X_numerical = np.array(numerical_features)
            X_categorical = np.array(categorical_features)
            
            # Normalizar features numéricas
            X_numerical_scaled = self.scaler.fit_transform(X_numerical)
            
            # Codificar features categóricas
            X_categorical_encoded = []
            for i, col in enumerate(['season', 'price_range', 'category', 'store']):
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                
                encoder = self.label_encoders[col]
                encoded_col = encoder.fit_transform(X_categorical[:, i])
                X_categorical_encoded.append(encoded_col)
            
            X_categorical_encoded = np.column_stack(X_categorical_encoded)
            
            # Combinar features
            X_combined = np.hstack([X_numerical_scaled, X_categorical_encoded])
            
            return X_combined, np.array([f.geek_score for f in features])
            
        except Exception as e:
            self.logger.error(f"Erro ao preparar features: {e}")
            raise
    
    async def train_model(self, training_data: TrainingData, 
                         model_name: str = 'random_forest') -> TrainingResult:
        """Treina um modelo específico"""
        try:
            start_time = datetime.now()
            self.logger.info(f"Iniciando treinamento do modelo {model_name}...")
            
            if model_name not in self.models:
                raise ValueError(f"Modelo {model_name} não disponível")
            
            # Preparar dados
            X, y = self._prepare_features(training_data.features)
            
            # Dividir dados de treinamento e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Treinar modelo
            model = self.models[model_name]
            model.fit(X_train, y_train)
            
            # Fazer predições
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            cv_score = cv_scores.mean()
            
            # Tempo de treinamento
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Feature importance (se disponível)
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_names = [
                    'price', 'geek_score', 'conversion_rate', 'click_rate', 
                    'engagement_rate', 'time_of_day', 'day_of_week', 
                    'category_popularity', 'store_reputation', 'title_length',
                    'has_discount', 'discount_percentage', 'season', 'price_range',
                    'category', 'store'
                ]
                feature_importance = dict(zip(feature_names, model.feature_importances_))
            
            # Criar métricas
            metrics = ModelMetrics(
                model_name=model_name,
                r2_score=r2,
                mse=mse,
                mae=mae,
                cross_val_score=cv_score,
                training_time=training_time,
                created_at=datetime.now()
            )
            
            # Salvar modelo
            model_path = self.models_path / f"{model_name}_model.pkl"
            scaler_path = self.models_path / f"{model_name}_scaler.pkl"
            encoders_path = self.models_path / f"{model_name}_encoders.pkl"
            
            joblib.dump(model, model_path)
            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.label_encoders, encoders_path)
            
            # Salvar métricas no banco
            await self._save_metrics(metrics, feature_importance)
            
            self.logger.info(f"Modelo {model_name} treinado com sucesso")
            self.logger.info(f"R² Score: {r2:.4f}, MSE: {mse:.4f}, MAE: {mae:.4f}")
            
            return TrainingResult(
                model_name=model_name,
                model_path=str(model_path),
                metrics=metrics,
                feature_importance=feature_importance,
                training_data_size=len(training_data.features),
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo {model_name}: {e}")
            raise
    
    async def train_all_models(self, training_data: TrainingData) -> List[TrainingResult]:
        """Treina todos os modelos disponíveis"""
        try:
            results = []
            
            for model_name in self.models.keys():
                try:
                    result = await self.train_model(training_data, model_name)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Erro ao treinar {model_name}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar todos os modelos: {e}")
            return []
    
    async def _save_metrics(self, metrics: ModelMetrics, 
                          feature_importance: Dict[str, float]):
        """Salva métricas no banco de dados"""
        try:
            db_path = self.models_path / "training_metrics.db"
            with sqlite3.connect(db_path) as conn:
                # Salvar métricas do modelo
                conn.execute("""
                    INSERT INTO model_metrics (
                        model_name, r2_score, mse, mae, cross_val_score, 
                        training_time, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.model_name, metrics.r2_score, metrics.mse,
                    metrics.mae, metrics.cross_val_score, metrics.training_time,
                    metrics.created_at
                ))
                
                # Salvar feature importance
                for feature, importance in feature_importance.items():
                    conn.execute("""
                        INSERT INTO feature_importance (
                            model_name, feature_name, importance, created_at
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        metrics.model_name, feature, importance, metrics.created_at
                    ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar métricas: {e}")
    
    async def get_best_model(self) -> Optional[str]:
        """Obtém o melhor modelo baseado nas métricas"""
        try:
            db_path = self.models_path / "training_metrics.db"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT model_name, AVG(r2_score) as avg_r2, 
                           AVG(cross_val_score) as avg_cv
                    FROM model_metrics 
                    GROUP BY model_name
                    ORDER BY avg_r2 DESC, avg_cv DESC
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row:
                    return row[0]
                
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter melhor modelo: {e}")
            return None
    
    async def get_model_metrics(self, model_name: str) -> List[ModelMetrics]:
        """Obtém métricas de um modelo específico"""
        try:
            db_path = self.models_path / "training_metrics.db"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT model_name, r2_score, mse, mae, cross_val_score,
                           training_time, created_at
                    FROM model_metrics 
                    WHERE model_name = ?
                    ORDER BY created_at DESC
                """, (model_name,))
                
                metrics = []
                for row in cursor.fetchall():
                    metrics.append(ModelMetrics(
                        model_name=row[0],
                        r2_score=row[1],
                        mse=row[2],
                        mae=row[3],
                        cross_val_score=row[4],
                        training_time=row[5],
                        created_at=datetime.fromisoformat(row[6])
                    ))
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas do modelo: {e}")
            return []
    
    async def get_feature_importance(self, model_name: str) -> Dict[str, float]:
        """Obtém feature importance de um modelo"""
        try:
            db_path = self.models_path / "training_metrics.db"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT feature_name, AVG(importance) as avg_importance
                    FROM feature_importance 
                    WHERE model_name = ?
                    GROUP BY feature_name
                    ORDER BY avg_importance DESC
                """, (model_name,))
                
                importance = {}
                for row in cursor.fetchall():
                    importance[row[0]] = row[1]
                
                return importance
                
        except Exception as e:
            self.logger.error(f"Erro ao obter feature importance: {e}")
            return {}
    
    def load_model(self, model_name: str):
        """Carrega um modelo treinado"""
        try:
            model_path = self.models_path / f"{model_name}_model.pkl"
            scaler_path = self.models_path / f"{model_name}_scaler.pkl"
            encoders_path = self.models_path / f"{model_name}_encoders.pkl"
            
            if not model_path.exists():
                raise FileNotFoundError(f"Modelo {model_name} não encontrado")
            
            model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoders = joblib.load(encoders_path)
            
            return model
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo {model_name}: {e}")
            raise
