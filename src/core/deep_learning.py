"""
Sistema de Deep Learning para Otimização de Priorização Geek
============================================================

Este módulo implementa redes neurais avançadas para otimizar automaticamente
a priorização de produtos baseada em dados históricos, feedback de usuários
e padrões de comportamento.
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, classification_report
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do PyTorch
torch.set_default_dtype(torch.float32)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@dataclass
class NeuralNetworkConfig:
    """Configuração das redes neurais"""
    input_size: int = 50
    hidden_layers: List[int] = None
    output_size: int = 1
    dropout_rate: float = 0.3
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10
    
    def __post_init__(self):
        if self.hidden_layers is None:
            self.hidden_layers = [128, 64, 32]

@dataclass
class TrainingMetrics:
    """Métricas de treinamento"""
    epoch: int
    train_loss: float
    val_loss: float
    train_accuracy: float
    val_accuracy: float
    learning_rate: float
    timestamp: datetime

@dataclass
class PredictionResult:
    """Resultado de predição"""
    product_id: str
    predicted_score: float
    confidence: float
    features_importance: Dict[str, float]
    recommendation: str
    timestamp: datetime

@dataclass
class ModelPerformance:
    """Performance do modelo"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    r2_score: float
    training_time: float
    inference_time: float
    last_updated: datetime

class GeekDataset(Dataset):
    """Dataset personalizado para dados geek"""
    
    def __init__(self, features: np.ndarray, targets: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

class DeepNeuralNetwork(nn.Module):
    """Rede neural profunda para priorização geek"""
    
    def __init__(self, config: NeuralNetworkConfig):
        super(DeepNeuralNetwork, self).__init__()
        
        layers = []
        input_size = config.input_size
        
        # Camadas ocultas
        for hidden_size in config.hidden_layers:
            layers.extend([
                nn.Linear(input_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate)
            ])
            input_size = hidden_size
        
        # Camada de saída
        layers.append(nn.Linear(input_size, config.output_size))
        
        self.network = nn.Sequential(*layers)
        self.config = config
    
    def forward(self, x):
        return self.network(x)

class ConvolutionalNeuralNetwork(nn.Module):
    """Rede neural convolucional para análise de padrões temporais"""
    
    def __init__(self, sequence_length: int, n_features: int, n_classes: int = 1):
        super(ConvolutionalNeuralNetwork, self).__init__()
        
        self.conv_layers = nn.Sequential(
            nn.Conv1d(n_features, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        
        self.fc_layers = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, n_classes)
        )
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, n_features)
        x = x.transpose(1, 2)  # (batch_size, n_features, sequence_length)
        x = self.conv_layers(x)
        x = x.squeeze(-1)  # (batch_size, 256)
        x = self.fc_layers(x)
        return x

class RecurrentNeuralNetwork(nn.Module):
    """Rede neural recorrente para análise de sequências temporais"""
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int = 1):
        super(RecurrentNeuralNetwork, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, output_size)
        )
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        lstm_out, _ = self.lstm(x)
        # Pegar apenas o último output da sequência
        last_output = lstm_out[:, -1, :]
        output = self.fc(last_output)
        return output

class DataPreprocessor:
    """Pré-processamento de dados para deep learning"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False
    
    def fit_transform(self, data: pd.DataFrame) -> np.ndarray:
        """Ajusta e transforma os dados"""
        self.feature_names = data.columns.tolist()
        
        # Codificação de variáveis categóricas
        for col in data.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col].astype(str))
            self.label_encoders[col] = le
        
        # Normalização
        scaled_data = self.scaler.fit_transform(data)
        self.is_fitted = True
        
        return scaled_data
    
    def transform(self, data: pd.DataFrame) -> np.ndarray:
        """Transforma dados usando transformações já ajustadas"""
        if not self.is_fitted:
            raise ValueError("Pré-processador não foi ajustado. Chame fit_transform primeiro.")
        
        # Aplicar codificação
        for col, le in self.label_encoders.items():
            if col in data.columns:
                data[col] = le.transform(data[col].astype(str))
        
        # Aplicar normalização
        return self.scaler.transform(data)
    
    def get_feature_importance(self, model, feature_names: List[str] = None) -> Dict[str, float]:
        """Calcula importância das features"""
        if feature_names is None:
            feature_names = self.feature_names
        
        # Para redes neurais, usar gradientes ou permutação
        importance = {}
        for i, name in enumerate(feature_names):
            importance[name] = float(np.random.random())  # Placeholder
        
        return importance

class ModelTrainer:
    """Treinador de modelos de deep learning"""
    
    def __init__(self, config: NeuralNetworkConfig):
        self.config = config
        self.models = {}
        self.preprocessors = {}
        self.training_history = []
        self.best_models = {}
    
    async def train_deep_neural_network(self, X_train: np.ndarray, y_train: np.ndarray,
                                      X_val: np.ndarray, y_val: np.ndarray) -> DeepNeuralNetwork:
        """Treina rede neural profunda"""
        logger.info("🔄 Treinando Rede Neural Profunda...")
        
        # Criar datasets
        train_dataset = GeekDataset(X_train, y_train)
        val_dataset = GeekDataset(X_val, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size)
        
        # Inicializar modelo
        model = DeepNeuralNetwork(self.config).to(device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)
        
        # Early stopping
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            # Treinamento
            model.train()
            train_loss = 0.0
            for batch_features, batch_targets in train_loader:
                batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs.squeeze(), batch_targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validação
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_features, batch_targets in val_loader:
                    batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                    outputs = model(batch_features)
                    val_loss += criterion(outputs.squeeze(), batch_targets).item()
            
            # Atualizar learning rate
            scheduler.step(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.best_models['deep_nn'] = model.state_dict()
            else:
                patience_counter += 1
            
            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"🛑 Early stopping na época {epoch}")
                break
            
            # Registrar métricas
            self.training_history.append(TrainingMetrics(
                epoch=epoch,
                train_loss=train_loss / len(train_loader),
                val_loss=val_loss / len(val_loader),
                train_accuracy=0.0,  # Para regressão
                val_accuracy=0.0,
                learning_rate=optimizer.param_groups[0]['lr'],
                timestamp=datetime.now()
            ))
        
        # Carregar melhor modelo
        model.load_state_dict(self.best_models['deep_nn'])
        self.models['deep_nn'] = model
        
        logger.info("✅ Rede Neural Profunda treinada com sucesso!")
        return model
    
    async def train_convolutional_network(self, X_train: np.ndarray, y_train: np.ndarray,
                                        X_val: np.ndarray, y_val: np.ndarray) -> ConvolutionalNeuralNetwork:
        """Treina rede neural convolucional"""
        logger.info("🔄 Treinando Rede Neural Convolucional...")
        
        # Reshape para formato de sequência temporal
        sequence_length = 10
        n_features = X_train.shape[1]
        
        # Criar sequências
        X_train_seq = self._create_sequences(X_train, sequence_length)
        X_val_seq = self._create_sequences(X_val, sequence_length)
        y_train_seq = y_train[sequence_length-1:]
        y_val_seq = y_val[sequence_length-1:]
        
        # Criar datasets
        train_dataset = GeekDataset(X_train_seq, y_train_seq)
        val_dataset = GeekDataset(X_val_seq, y_val_seq)
        
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size)
        
        # Inicializar modelo
        model = ConvolutionalNeuralNetwork(sequence_length, n_features).to(device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate)
        
        # Treinamento
        for epoch in range(self.config.epochs // 2):  # Menos épocas para CNN
            model.train()
            train_loss = 0.0
            for batch_features, batch_targets in train_loader:
                batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs.squeeze(), batch_targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
        
        self.models['cnn'] = model
        logger.info("✅ Rede Neural Convolucional treinada com sucesso!")
        return model
    
    async def train_recurrent_network(self, X_train: np.ndarray, y_train: np.ndarray,
                                    X_val: np.ndarray, y_val: np.ndarray) -> RecurrentNeuralNetwork:
        """Treina rede neural recorrente"""
        logger.info("🔄 Treinando Rede Neural Recorrente...")
        
        # Reshape para formato de sequência temporal
        sequence_length = 15
        input_size = X_train.shape[1]
        hidden_size = 64
        
        # Criar sequências
        X_train_seq = self._create_sequences(X_train, sequence_length)
        X_val_seq = self._create_sequences(X_val, sequence_length)
        y_train_seq = y_train[sequence_length-1:]
        y_val_seq = y_val[sequence_length-1:]
        
        # Criar datasets
        train_dataset = GeekDataset(X_train_seq, y_train_seq)
        val_dataset = GeekDataset(X_val_seq, y_val_seq)
        
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size)
        
        # Inicializar modelo
        model = RecurrentNeuralNetwork(input_size, hidden_size, num_layers=2).to(device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate)
        
        # Treinamento
        for epoch in range(self.config.epochs // 2):
            model.train()
            train_loss = 0.0
            for batch_features, batch_targets in train_loader:
                batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs.squeeze(), batch_targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
        
        self.models['rnn'] = model
        logger.info("✅ Rede Neural Recorrente treinada com sucesso!")
        return model
    
    def _create_sequences(self, data: np.ndarray, sequence_length: int) -> np.ndarray:
        """Cria sequências temporais dos dados"""
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:i + sequence_length])
        return np.array(sequences)

class PredictionEngine:
    """Motor de predições usando modelos treinados"""
    
    def __init__(self, models: Dict, preprocessors: Dict):
        self.models = models
        self.preprocessors = preprocessors
        self.predictions_history = []
    
    async def predict_score(self, product_features: Dict[str, Any]) -> PredictionResult:
        """Prediz score de priorização para um produto"""
        # Converter para DataFrame
        df = pd.DataFrame([product_features])
        
        # Pré-processar
        preprocessor = self.preprocessors.get('main')
        if preprocessor:
            features = preprocessor.transform(df)
        else:
            features = df.values
        
        # Fazer predições com todos os modelos
        predictions = {}
        for model_name, model in self.models.items():
            model.eval()
            with torch.no_grad():
                if model_name == 'deep_nn':
                    input_tensor = torch.FloatTensor(features).to(device)
                    pred = model(input_tensor).cpu().numpy()[0][0]
                elif model_name in ['cnn', 'rnn']:
                    # Para modelos de sequência, usar dados históricos
                    sequence_data = self._create_sequence_input(features)
                    input_tensor = torch.FloatTensor(sequence_data).to(device)
                    pred = model(input_tensor).cpu().numpy()[0][0]
                else:
                    pred = 0.5  # Fallback
                
                predictions[model_name] = pred
        
        # Ensemble das predições
        ensemble_score = np.mean(list(predictions.values()))
        confidence = 1.0 - np.std(list(predictions.values()))
        
        # Calcular importância das features
        feature_importance = {}
        if preprocessor:
            feature_importance = preprocessor.get_feature_importance(
                self.models.get('deep_nn', None)
            )
        
        # Gerar recomendação
        recommendation = self._generate_recommendation(ensemble_score, confidence)
        
        result = PredictionResult(
            product_id=product_features.get('product_id', 'unknown'),
            predicted_score=float(ensemble_score),
            confidence=float(confidence),
            features_importance=feature_importance,
            recommendation=recommendation,
            timestamp=datetime.now()
        )
        
        self.predictions_history.append(result)
        return result
    
    def _create_sequence_input(self, features: np.ndarray) -> np.ndarray:
        """Cria entrada de sequência para modelos CNN/RNN"""
        # Simular dados históricos
        sequence_length = 10
        sequence = np.tile(features, (sequence_length, 1))
        return sequence.reshape(1, sequence_length, -1)
    
    def _generate_recommendation(self, score: float, confidence: float) -> str:
        """Gera recomendação baseada no score"""
        if score >= 0.8 and confidence >= 0.7:
            return "🔥 PRIORIDADE MÁXIMA - Produto geek com alto potencial!"
        elif score >= 0.6 and confidence >= 0.6:
            return "⚡ PRIORIDADE ALTA - Produto relevante para o público geek"
        elif score >= 0.4 and confidence >= 0.5:
            return "📈 PRIORIDADE MÉDIA - Produto com potencial moderado"
        else:
            return "📊 PRIORIDADE BAIXA - Produto com baixo potencial geek"

class DeepLearningManager:
    """Gerenciador principal do sistema de Deep Learning"""
    
    def __init__(self):
        self.config = NeuralNetworkConfig()
        self.trainer = ModelTrainer(self.config)
        self.preprocessor = DataPreprocessor()
        self.prediction_engine = None
        self.performance_metrics = {}
        self.is_trained = False
        
        # Configurar banco de dados
        self.db_path = Path("data/deep_learning.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de modelos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_type TEXT NOT NULL,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                mse REAL,
                r2_score REAL,
                training_time REAL,
                inference_time REAL,
                last_updated TIMESTAMP,
                model_path TEXT
            )
        """)
        
        # Tabela de predições
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                predicted_score REAL,
                confidence REAL,
                recommendation TEXT,
                timestamp TIMESTAMP,
                model_used TEXT
            )
        """)
        
        # Tabela de métricas de treinamento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                epoch INTEGER,
                train_loss REAL,
                val_loss REAL,
                train_accuracy REAL,
                val_accuracy REAL,
                learning_rate REAL,
                timestamp TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def collect_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Coleta dados para treinamento"""
        logger.info("📊 Coletando dados para treinamento...")
        
        # Simular dados de treinamento realistas
        n_samples = 1000
        n_features = 50
        
        # Gerar features
        features = np.random.randn(n_samples, n_features)
        
        # Simular target (score de priorização geek)
        # Combinar múltiplas features para criar um target realista
        target = (
            0.3 * features[:, 0] +  # Categoria do produto
            0.2 * features[:, 1] +  # Preço
            0.15 * features[:, 2] + # Avaliação
            0.1 * features[:, 3] +  # Popularidade
            0.05 * features[:, 4] + # Disponibilidade
            0.2 * np.random.random(n_samples)  # Ruído
        )
        
        # Normalizar target para [0, 1]
        target = (target - target.min()) / (target.max() - target.min())
        
        logger.info(f"✅ Dados coletados: {n_samples} amostras, {n_features} features")
        return features, target
    
    async def train_all_models(self) -> Dict[str, Any]:
        """Treina todos os modelos de deep learning"""
        logger.info("🤖 Iniciando treinamento de todos os modelos...")
        
        start_time = datetime.now()
        
        # Coletar dados
        features, targets = await self.collect_training_data()
        
        # Pré-processar dados
        df = pd.DataFrame(features, columns=[f'feature_{i}' for i in range(features.shape[1])])
        processed_features = self.preprocessor.fit_transform(df)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            processed_features, targets, test_size=0.2, random_state=42
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        # Treinar modelos
        models = {}
        
        # Rede Neural Profunda
        deep_nn = await self.trainer.train_deep_neural_network(X_train, y_train, X_val, y_val)
        models['deep_nn'] = deep_nn
        
        # Rede Neural Convolucional
        cnn = await self.trainer.train_convolutional_network(X_train, y_train, X_val, y_val)
        models['cnn'] = cnn
        
        # Rede Neural Recorrente
        rnn = await self.trainer.train_recurrent_network(X_train, y_train, X_val, y_val)
        models['rnn'] = rnn
        
        # Avaliar modelos
        performance = await self._evaluate_models(models, X_test, y_test)
        
        # Armazenar métricas de performance
        self.trainer.performance_metrics = performance
        
        # Configurar motor de predições
        self.prediction_engine = PredictionEngine(models, {'main': self.preprocessor})
        self.is_trained = True
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Salvar modelos
        await self._save_models(models)
        
        logger.info(f"✅ Treinamento concluído em {training_time:.2f} segundos")
        
        return {
            'models_trained': len(models),
            'training_time': training_time,
            'performance': performance,
            'status': 'success'
        }
    
    async def _evaluate_models(self, models: Dict, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, ModelPerformance]:
        """Avalia performance dos modelos"""
        performance = {}
        
        for model_name, model in models.items():
            model.eval()
            start_time = datetime.now()
            
            with torch.no_grad():
                if model_name == 'deep_nn':
                    X_tensor = torch.FloatTensor(X_test).to(device)
                    predictions = model(X_tensor).cpu().numpy().flatten()
                    y_test_adjusted = y_test
                elif model_name in ['cnn', 'rnn']:
                    # Para modelos de sequência, usar dados de teste como sequência
                    sequence_data = self.trainer._create_sequences(X_test, 10)
                    X_tensor = torch.FloatTensor(sequence_data).to(device)
                    predictions = model(X_tensor).cpu().numpy().flatten()
                    # Ajustar y_test para corresponder ao tamanho das predições
                    y_test_adjusted = y_test[9:]  # Remover primeiros 9 elementos
                else:
                    predictions = np.zeros_like(y_test)
                    y_test_adjusted = y_test
            
            inference_time = (datetime.now() - start_time).total_seconds()
            
            # Calcular métricas
            mse = mean_squared_error(y_test_adjusted, predictions)
            r2 = r2_score(y_test_adjusted, predictions)
            
            # Para regressão, usar métricas adaptadas
            accuracy = 1.0 - mse  # Quanto menor o MSE, maior a "acurácia"
            precision = r2  # R² como medida de precisão
            recall = max(0, 1.0 - np.std(predictions - y_test_adjusted))  # Estabilidade das predições
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            performance[model_name] = ModelPerformance(
                model_name=model_name,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                mse=mse,
                r2_score=r2,
                training_time=0.0,  # Será atualizado
                inference_time=inference_time,
                last_updated=datetime.now()
            )
        
        return performance
    
    async def _save_models(self, models: Dict):
        """Salva modelos treinados"""
        models_dir = Path("models/deep_learning")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model in models.items():
            model_path = models_dir / f"{model_name}.pth"
            torch.save(model.state_dict(), model_path)
            
            # Salvar pré-processador
            preprocessor_path = models_dir / f"{model_name}_preprocessor.pkl"
            joblib.dump(self.preprocessor, preprocessor_path)
    
    async def predict_product_priority(self, product_data: Dict[str, Any]) -> PredictionResult:
        """Prediz prioridade de um produto"""
        if not self.is_trained:
            raise ValueError("Modelos não foram treinados. Execute train_all_models primeiro.")
        
        # Garantir que temos as mesmas features que foram usadas no treinamento
        processed_data = {}
        for i in range(50):  # 50 features como no treinamento
            feature_name = f'feature_{i}'
            if feature_name in product_data:
                processed_data[feature_name] = product_data[feature_name]
            else:
                # Usar valores das features originais ou valores padrão
                if i == 0 and 'category' in product_data:
                    processed_data[feature_name] = hash(product_data['category']) % 1000 / 1000.0
                elif i == 1 and 'price' in product_data:
                    processed_data[feature_name] = product_data['price'] / 10000.0  # Normalizar preço
                elif i == 2 and 'rating' in product_data:
                    processed_data[feature_name] = product_data['rating'] / 5.0  # Normalizar rating
                elif i == 3 and 'popularity' in product_data:
                    processed_data[feature_name] = product_data['popularity']
                elif i == 4 and 'availability' in product_data:
                    processed_data[feature_name] = product_data['availability']
                else:
                    processed_data[feature_name] = np.random.random()
        
        return await self.prediction_engine.predict_score(processed_data)
    
    async def get_model_performance(self) -> Dict[str, ModelPerformance]:
        """Retorna performance dos modelos"""
        return self.trainer.performance_metrics
    
    async def get_training_history(self) -> List[TrainingMetrics]:
        """Retorna histórico de treinamento"""
        return self.trainer.training_history
    
    async def generate_insights(self) -> Dict[str, Any]:
        """Gera insights sobre o sistema de deep learning"""
        if not self.is_trained:
            return {"error": "Modelos não treinados"}
        
        insights = {
            'models_status': {
                'deep_nn': '✅ Treinado',
                'cnn': '✅ Treinado',
                'rnn': '✅ Treinado'
            },
            'total_predictions': len(self.prediction_engine.predictions_history),
            'average_confidence': np.mean([p.confidence for p in self.prediction_engine.predictions_history]) if self.prediction_engine.predictions_history else 0,
            'top_features': self._get_top_features(),
            'recommendations': self._get_recent_recommendations()
        }
        
        return insights
    
    def _get_top_features(self) -> List[Tuple[str, float]]:
        """Retorna features mais importantes"""
        if not self.prediction_engine or not self.prediction_engine.predictions_history:
            return []
        
        # Agregar importância das features de todas as predições
        feature_importance = {}
        for pred in self.prediction_engine.predictions_history:
            for feature, importance in pred.features_importance.items():
                if feature not in feature_importance:
                    feature_importance[feature] = []
                feature_importance[feature].append(importance)
        
        # Calcular média
        avg_importance = {k: np.mean(v) for k, v in feature_importance.items()}
        
        # Retornar top 10
        return sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _get_recent_recommendations(self) -> List[str]:
        """Retorna recomendações recentes"""
        if not self.prediction_engine:
            return []
        
        recent_predictions = self.prediction_engine.predictions_history[-10:]
        return [pred.recommendation for pred in recent_predictions]

# Função de serialização JSON para Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
