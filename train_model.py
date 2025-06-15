import os
import pandas as pd
from pymongo import MongoClient
from xgboost import XGBClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Variável de ambiente MONGO_URI não definida")

try:
    client = MongoClient(MONGO_URI)
    db = client["crimes_db"]  # Banco de dados
    colecao = db["crimes"]    # Coleção
    print("✅ Conectado ao MongoDB para treinamento")
except Exception as e:
    print(f"❌ Falha na conexão com MongoDB: {e}")
    raise

# Recuperar dados
dados = list(colecao.find({}, {"_id": 0}))

# Preparar DataFrame flat
lista = []
for d in dados:
    # Tratamento defensivo para estrutura de dados
    vitima = d.get("vitima", {})
    lista.append({
        "idade": vitima.get("idade"),
        "etnia": vitima.get("etnia"),
        "localizacao": d.get("localizacao"),
        "tipo_do_caso": d.get("tipo_do_caso")
    })

df = pd.DataFrame(lista).dropna()

if df.empty:
    raise ValueError("Nenhum dado válido para treinamento")

print(f"✅ Dados carregados: {len(df)} registros")

# Variáveis explicativas e alvo
X = df[["idade", "etnia", "localizacao"]]
y = df["tipo_do_caso"]

# Encode da variável alvo
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Pipeline
categorical_features = ["etnia", "localizacao"]
numeric_features = ["idade"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ("num", "passthrough", numeric_features)
    ]
)

# Usar parâmetros atualizados do XGBoost
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(eval_metric='mlogloss', enable_categorical=True))
])

# Treinar
pipeline.fit(X, y_encoded)

# Salvar pipeline + label encoder
with open("model.pkl", "wb") as f:
    pickle.dump({
        "pipeline": pipeline,
        "label_encoder": label_encoder
    }, f)

print(f"✅ Modelo treinado com {len(df)} amostras e salvo em model.pkl")
print(f"Classes: {label_encoder.classes_}")