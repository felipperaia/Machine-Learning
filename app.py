import os
import warnings
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import random
import pickle
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Suprimir warnings do XGBoost
warnings.filterwarnings("ignore", category=UserWarning, module="xgboost.*")

app = Flask(__name__)
CORS(app)

# Carrega variáveis do arquivo .env
load_dotenv()

# MongoDB Connection com tratamento de erros
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("⚠️  MONGO_URI não definida no ambiente")
    MONGO_URI = "mongodb://localhost:27017/"  # Fallback para desenvolvimento

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Testa a conexão
    client.admin.command('ismaster')
    print("✅ Conectado ao MongoDB")
    db = client.get_database("crimes_db")  # Usar get_database para flexibilidade
    colecao = db["crimes"]
except ConnectionFailure as e:
    print(f"❌ Falha na conexão com MongoDB: {e}")
    client = None
    db = None
    colecao = None
except Exception as e:
    print(f"❌ Erro inesperado ao conectar ao MongoDB: {e}")
    client = None
    db = None
    colecao = None

# Carrega o modelo com tratamento de erros
try:
    with open("model.pkl", "rb") as f:
        data = pickle.load(f)
        modelo = data["pipeline"]
        label_encoder = data["label_encoder"]
    print("✅ Modelo carregado com sucesso")
except Exception as e:
    print(f"❌ Erro ao carregar o modelo: {e}")
    modelo = None
    label_encoder = None

@dataclass
class Vitima:
    etnia: str
    idade: int

@dataclass
class Caso:
    data_do_caso: str
    tipo_do_caso: str
    localizacao: str
    vitima: Vitima

    def to_dict(self):
        return {
            "data_do_caso": self.data_do_caso,
            "tipo_do_caso": self.tipo_do_caso,
            "localizacao": self.localizacao,
            "vitima": asdict(self.vitima)
        }

def validar_caso_json(data):
    try:
        vitima = data["vitima"]
        assert isinstance(vitima, dict)
        assert all(k in vitima for k in ("etnia", "idade"))
        datetime.fromisoformat(data["data_do_caso"])
        assert isinstance(data["tipo_do_caso"], str)
        assert isinstance(data["localizacao"], str)
    except:
        return False
    return True

def gerar_dados_aleatorios(n=20):
    tipos_casos = ["Furto", "Assalto", "Violência doméstica", "Tráfico"]
    locais = ["Centro", "Bairro A", "Bairro B", "Zona Rural"]
    etnias = ["Branca", "Preta", "Parda", "Indígena", "Amarela"]
    casos = []
    base_date = datetime.now()
    for i in range(n):
        data_caso = (base_date - timedelta(days=random.randint(0, 365))).date().isoformat()
        caso = Caso(
            data_do_caso=data_caso,
            tipo_do_caso=random.choice(tipos_casos),
            localizacao=random.choice(locais),
            vitima=Vitima(
                etnia=random.choice(etnias),
                idade=random.randint(1, 90)
            )
        )
        casos.append(caso.to_dict())
    return casos

@app.route('/api/casos', methods=['GET'])
def listar_casos():
    if colecao is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
    documentos = list(colecao.find({}, {"_id": 0}))
    return jsonify(documentos), 200

@app.route('/api/casos', methods=['POST'])
def criar_caso():
    if colecao is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
    data = request.get_json()
    if not data or not validar_caso_json(data):
        abort(400, "JSON inválido ou campos faltando.")
    colecao.insert_one(data)
    return jsonify({"message": "Caso criado com sucesso"}), 201

@app.route('/api/casos/<string:data_caso>', methods=['GET'])
def buscar_caso(data_caso):
    if colecao is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
    caso = colecao.find_one({"data_do_caso": data_caso}, {"_id": 0})
    if not caso:
        abort(404, "Caso não encontrado.")
    return jsonify(caso), 200

@app.route('/api/casos/<string:data_caso>', methods=['DELETE'])
def deletar_caso(data_caso):
    if colecao is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
    resultado = colecao.delete_one({"data_do_caso": data_caso})
    if resultado.deleted_count == 0:
        abort(404, "Caso não encontrado.")
    return jsonify({"message": "Caso deletado"}), 200

@app.route('/api/associacoes', methods=['GET'])
def associacoes():
    if colecao is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
    documentos = list(colecao.find({}, {"_id": 0}))
    if not documentos:
        return jsonify({"message": "Sem dados na coleção"}), 400
    lista = []
    for d in documentos:
        vitima = d.get("vitima", {})
        lista.append({
            "idade": vitima.get("idade"),
            "etnia": vitima.get("etnia"),
            "localizacao": d.get("localizacao"),
            "tipo_do_caso": d.get("tipo_do_caso")
        })
    df = pd.DataFrame(lista).dropna()
    try:
        X = df[["idade", "etnia", "localizacao"]]
        return jsonify({"message": "Endpoint pronto para implementar análise"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao processar modelo: {str(e)}"}), 500

@app.route('/api/predizer', methods=['POST'])
def predizer():
    if modelo is None or label_encoder is None:
        return jsonify({"error": "Modelo não carregado"}), 500
    dados = request.get_json()
    if not dados or not all(k in dados for k in ("idade", "etnia", "localizacao")):
        return jsonify({"erro": "JSON inválido. Esperado: idade, etnia, localizacao"}), 400
    try:
        df = pd.DataFrame([dados])
        y_prob = modelo.predict_proba(df)[0]
        y_pred_encoded = modelo.predict(df)[0]
        y_pred = label_encoder.inverse_transform([y_pred_encoded])[0]
        classes = label_encoder.classes_
        resultado = {
            "classe_predita": y_pred,
            "probabilidades": {classe: round(prob, 4) for classe, prob in zip(classes, y_prob)}
        }
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao fazer predição: {str(e)}"}), 500

@app.route('/api/modelo/coeficientes', methods=['GET'])
def coeficientes_modelo():
    if modelo is None:
        return jsonify({"error": "Modelo não carregado"}), 500
    try:
        preprocessor = modelo.named_steps['preprocessor']
        classifier = modelo.named_steps['classifier']

        cat_encoder = preprocessor.named_transformers_['cat']
        cat_features = cat_encoder.get_feature_names_out(preprocessor.transformers_[0][2])
        numeric_features = preprocessor.transformers_[1][2]
        all_features = list(cat_features) + list(numeric_features)

        importancias = classifier.feature_importances_
        features_importances = {
            feature: float(importance)
            for feature, importance in zip(all_features, importancias)
        }

        print("Features importances a serem enviadas:", features_importances)
        return jsonify(features_importances), 200
    except Exception as e:
        print("ERRO:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({
        "status": "online",
        "database": "connected" if colecao is not None else "disconnected",
        "model_loaded": modelo is not None
    }), 200

if __name__ == "__main__":
    if colecao is not None:
        try:
            if colecao.count_documents({}) == 0:
                print("Coleção vazia, inserindo dados aleatórios iniciais...")
                dados_iniciais = gerar_dados_aleatorios(20)
                colecao.insert_many(dados_iniciais)
                print("Dados inseridos com sucesso.")
            else:
                print("Coleção já possui dados. Nenhuma inserção inicial foi feita.")
        except Exception as e:
            print(f"Erro ao verificar/inicializar dados: {e}")
    else:
        print("⚠️  Não foi possível conectar ao MongoDB. Dados iniciais não serão inseridos.")

    # Configuração CORRETA para o Render
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)