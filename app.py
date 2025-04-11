from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import json, os

app = Flask(__name__)

# Caminhos para arquivos de conhecimento
personagens = ["z4quel", "l3ticia", "symbio"]
conhecimento = {p: f"data/{p}.json" for p in personagens}

# Dados dinâmicos
mensagens_reuniao = []
nivel_autonomia = {p: 5 for p in personagens}
nivel_autonomia["symbio"] = 6

@app.route('/')
def index():
    return render_template("index.html", personagens=personagens)

@app.route('/sala', methods=['POST'])
def sala():
    msg = request.json.get("msg")
    remetente = request.json.get("remetente")
    resposta = f"{remetente}: Ainda estou aprendendo a responder isso."  # Mock

    mensagens_reuniao.append({"user": remetente, "resposta": resposta})
    return jsonify({"resposta": resposta, "mensagens": mensagens_reuniao})

@app.route('/nivel', methods=['POST'])
def nivel():
    dados = request.json
    ia = dados.get("ia")
    nivel = dados.get("nivel")
    nivel_autonomia[ia] = nivel
    return jsonify({"msg": f"Nível de autonomia de {ia} definido como {nivel}"})

@app.route('/monitoramento')
def monitoramento():
    # Simulação de dados
    return jsonify({
        "status": "OK",
        "autonomias": nivel_autonomia,
        "ativas": personagens
    })

# 🔥 Servidor com waitress
if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)
