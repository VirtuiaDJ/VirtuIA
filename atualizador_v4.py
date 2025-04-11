import os
import json
import shutil
import zipfile
import requests
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis do ambiente (opcional)
load_dotenv()

# Chave de API do DeepSeek (pode ser definida via .env)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-5219276b9cf743c5abc9d7148d31ae71")

def atualizar_arquivo(caminho, conteudo):
    pasta = os.path.dirname(caminho)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo.strip() if isinstance(conteudo, str) else str(conteudo))
    print(f"✅ Arquivo criado/atualizado: {caminho}")

# Estrutura final do projeto VirtuAI Premium v4.0
arquivos = {
    # Arquivo principal com endpoints para chat, treinamento, monitoramento, reuniões e configuração de autonomia.
    "app.py": r"""
from flask import Flask, render_template, request, jsonify, g
import os, json, sqlite3, requests
from datetime import datetime
from deepseek_integration import consulta_deepseek
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
DATABASE = 'virtuai.db'
app.secret_key = 'sua-chave-secreta'

# Banco de dados
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open("schema.sql", "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.commit()

# Funções para manipular dados das IAs
def carregar_ia(nome_ia):
    caminho = os.path.join("data", f"{nome_ia}.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return {"nome": nome_ia, "respostas": {}, "memoria": [], "advanced": {}}

def salvar_ia(nome_ia, dados):
    caminho = os.path.join("data", f"{nome_ia}.json")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)

def responder_ia(mensagem, ia_nome):
    if "detalhar" in mensagem.lower():
        resposta_deep = consulta_deepseek(mensagem)
        if resposta_deep:
            return f"{ia_nome.capitalize()} (DeepSeek): {resposta_deep}"
    ia = carregar_ia(ia_nome)
    msg = mensagem.lower().strip()
    for chave, resp in ia.get("respostas", {}).items():
        if chave in msg:
            return f"{ia_nome.capitalize()}: {resp}"
    if ia.get("advanced", {}).get("apresentacao"):
        return f"{ia_nome.capitalize()} (Avançado): {ia['advanced']['apresentacao']}"
    return f"{ia_nome.capitalize()}: Ainda estou aprendendo a responder isso."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    dados = request.get_json()
    ia = dados.get("ia")
    mensagem = dados.get("mensagem")
    resposta = responder_ia(mensagem, ia)
    
    db = get_db()
    db.execute("INSERT INTO chat_logs (ia, mensagem, resposta, timestamp) VALUES (?, ?, ?, ?)",
               (ia, mensagem, resposta, datetime.now().isoformat()))
    db.commit()
    
    ia_data = carregar_ia(ia)
    ia_data["memoria"].append({"pergunta": mensagem, "resposta": resposta})
    salvar_ia(ia, ia_data)
    
    return jsonify({"resposta": resposta})

@app.route("/treinar", methods=["POST"])
def treinar():
    dados = request.get_json()
    ia = dados.get("ia")
    pergunta = dados.get("pergunta").lower().strip()
    resposta = dados.get("resposta")
    ia_data = carregar_ia(ia)
    ia_data.setdefault("respostas", {})
    ia_data["respostas"][pergunta] = resposta
    salvar_ia(ia, ia_data)
    return jsonify({"resultado": f"{ia.capitalize()} treinada com sucesso!"})

@app.route("/treinar_deepseek", methods=["POST"])
def treinar_deepseek():
    dados = request.get_json()
    ia = dados.get("ia")
    mensagem = dados.get("mensagem")
    resposta_deep = consulta_deepseek(mensagem)
    ia_data = carregar_ia(ia)
    ia_data.setdefault("respostas", {})
    ia_data["respostas"][mensagem.lower()] = resposta_deep
    salvar_ia(ia, ia_data)
    return jsonify({"resultado": f"{ia.capitalize()} treinada via DeepSeek."})

@app.route("/configuracoes", methods=["POST"])
def configuracoes():
    dados = request.get_json()
    config_path = os.path.join("config", "autonomia.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    return jsonify({"resultado": "Configurações atualizadas com sucesso!"})

@app.route("/api/monitoramento")
def monitoramento():
    db = get_db()
    cursor = db.execute("SELECT COUNT(*) FROM chat_logs")
    total_msgs = cursor.fetchone()[0]
    dados = {
        "total_mensagens": total_msgs,
        "ultima_atualizacao": datetime.now().isoformat(),
        "niveis": {
            "z4quel": 5,
            "l3ticia": 5,
            "symbio": 6
        }
    }
    return jsonify(dados)

# Agendamento de Treinamento Contínuo e Simulação de Reuniões entre IAs
def treinamento_continuo():
    for ia in ["z4quel", "l3ticia", "symbio"]:
        print(f"[Treinamento Contínuo] Executado para {ia} em {datetime.now().isoformat()}")
        # Aqui, ações extras podem ser executadas: geração de relatórios, feedback, etc.

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=treinamento_continuo, trigger="interval", minutes=5)
scheduler.start()

# NGROK Integration (Opção Automática ou Manual)
# Para ativar o túnel NGROK automaticamente, descomente o bloco abaixo:
# import subprocess
# subprocess.Popen("ngrok http 5000", shell=True)
# print("NGROK iniciado, verifique a URL pública no terminal.")

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
""",
    "schema.sql": r"""
DROP TABLE IF EXISTS chat_logs;
CREATE TABLE chat_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ia TEXT NOT NULL,
  mensagem TEXT NOT NULL,
  resposta TEXT NOT NULL,
  timestamp TEXT NOT NULL
);
""",
    "requirements.txt": r"""Flask
python-dotenv
requests
APScheduler""",
    "deepseek_integration.py": r"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-5219276b9cf743c5abc9d7148d31ae71")

def consulta_deepseek(mensagem):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Responda de forma objetiva, clara e em português."},
            {"role": "user", "content": mensagem}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"[DeepSeek Erro {response.status_code}]"
    except Exception as e:
        return f"[DeepSeek Exceção: {e}]"
""",
    "templates/index.html": r"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <title>VirtuIA Premium - Hub</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
  <link rel="stylesheet" href="/static/css/style.css" />
</head>
<body class="bg-dark text-light">
  <nav class="navbar navbar-expand-lg navbar-dark bg-secondary">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">VirtuIA Premium</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
    </div>
  </nav>
  <div class="container my-4">
    <h1 class="text-center mb-4">VirtuIA – Hub de IAs</h1>
    <ul class="nav nav-tabs" id="myTab" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="tab-z4quel" data-bs-toggle="tab" data-bs-target="#pane-z4quel" type="button" role="tab">Z4quel</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-l3ticia" data-bs-toggle="tab" data-bs-target="#pane-l3ticia" type="button" role="tab">L3ticia</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-symbio" data-bs-toggle="tab" data-bs-target="#pane-symbio" type="button" role="tab">Symbio</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-reuniao" data-bs-toggle="tab" data-bs-target="#pane-reuniao" type="button" role="tab">Sala de Reunião</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-monitoramento" data-bs-toggle="tab" data-bs-target="#pane-monitoramento" type="button" role="tab">Monitoramento</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-treinamento" data-bs-toggle="tab" data-bs-target="#pane-treinamento" type="button" role="tab">Treinamento</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-clientes" data-bs-toggle="tab" data-bs-target="#pane-clientes" type="button" role="tab">Clientes</button>
      </li>
    </ul>
    <div class="tab-content mt-3" id="myTabContent">
      <!-- Aba Z4quel -->
      <div class="tab-pane fade show active" id="pane-z4quel" role="tabpanel">
        <div class="card bg-secondary p-3">
          <h3>Z4quel – Sala Individual</h3>
          <div id="chat-z4quel" class="chat-box mb-3"></div>
          <div class="input-group">
            <input type="text" class="form-control" id="msg-z4quel" placeholder="Digite sua mensagem para Z4quel..." />
            <button class="btn btn-success" onclick="enviarMensagem('z4quel')">Enviar</button>
          </div>
        </div>
      </div>
      <!-- Aba L3ticia -->
      <div class="tab-pane fade" id="pane-l3ticia" role="tabpanel">
        <div class="card bg-secondary p-3">
          <h3>L3ticia – Sala Individual</h3>
          <div id="chat-l3ticia" class="chat-box mb-3"></div>
          <div class="input-group">
            <input type="text" class="form-control" id="msg-l3ticia" placeholder="Digite sua mensagem para L3ticia..." />
            <button class="btn btn-success" onclick="enviarMensagem('l3ticia')">Enviar</button>
          </div>
        </div>
      </div>
      <!-- Aba Symbio -->
      <div class="tab-pane fade" id="pane-symbio" role="tabpanel">
        <div class="card bg-secondary p-3">
          <h3>Symbio – Sala Individual</h3>
          <div id="chat-symbio" class="chat-box mb-3"></div>
          <div class="input-group">
            <input type="text" class="form-control" id="msg-symbio" placeholder="Digite sua mensagem para Symbio..." />
            <button class="btn btn-success" onclick="enviarMensagem('symbio')">Enviar</button>
          </div>
        </div>
      </div>
      <!-- Aba Sala de Reunião -->
      <div class="tab-pane fade" id="pane-reuniao" role="tabpanel">
        <div class="card bg-dark p-3">
          <h3>Sala de Reunião – Interação entre IAs</h3>
          <div id="chat-reuniao" class="chat-box mb-3"></div>
          <div class="input-group">
            <input type="text" class="form-control" id="msg-reuniao" placeholder="Envie uma mensagem para a reunião..." />
            <button class="btn btn-info" onclick="enviarReuniao()">Enviar</button>
          </div>
        </div>
      </div>
      <!-- Aba Monitoramento -->
      <div class="tab-pane fade" id="pane-monitoramento" role="tabpanel">
        <div class="card bg-secondary p-3">
          <h3>Monitoramento em Tempo Real</h3>
          <canvas id="grafico-monitoramento" width="400" height="200"></canvas>
          <div id="monitoramento-texto" class="mt-3">
            <p>Aguardando dados de monitoramento...</p>
          </div>
        </div>
      </div>
      <!-- Aba Treinamento -->
      <div class="tab-pane fade" id="pane-treinamento" role="tabpanel">
        <div class="card bg-secondary p-3">
          <h3>Treinamento Avançado</h3>
          <p>Atualize o conhecimento das IAs com informações profissionais e apresentações.</p>
          <div class="input-group">
            <input type="text" class="form-control" id="treinar-msg" placeholder="Digite um treinamento..." />
            <select class="form-select" id="treinar-ia">
              <option value="z4quel">Z4quel</option>
              <option value="l3ticia">L3ticia</option>
              <option value="symbio">Symbio</option>
            </select>
            <button class="btn btn-warning" onclick="treinarDeep()">Treinar</button>
          </div>
        </div>
      </div>
      <!-- Aba Clientes -->
      <div class="tab-pane fade" id="pane-clientes" role="tabpanel">
        <div class="card bg-secondary p-3">
          <h3>Área de Clientes</h3>
          <p>Acesse seu histórico, tarefas e atendimento direto com as IAs.</p>
          <!-- Funcionalidades de login e histórico poderão ser integradas futuramente -->
        </div>
      </div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="/static/js/script.js"></script>
</body>
</html>
""",
    "static/css/style.css": r"""
body {
  background-color: #1F2937;
  color: #E5E7EB;
  font-family: 'Segoe UI', sans-serif;
  margin: 0;
  padding: 0;
}
.navbar {
  background-color: #111827;
}
.container {
  margin-top: 20px;
}
.chat-box {
  background-color: #111827;
  border: 1px solid #374151;
  border-radius: 5px;
  padding: 10px;
  height: 250px;
  overflow-y: auto;
  margin-bottom: 10px;
}
.card {
  margin-top: 20px;
  padding: 15px;
}
""",
    "static/js/script.js": r"""
// Atalho para envio com a tecla Enter
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if(this.id.startsWith("msg-")){
          let ia = this.id.split("-")[1];
          enviarMensagem(ia);
        } else if(this.id === "msg-reuniao"){
          enviarReuniao();
        }
      }
    });
  });
});

function enviarMensagem(ia) {
  let inputId = "msg-" + ia;
  let msg = document.getElementById(inputId).value;
  let chatBox = document.getElementById("chat-" + ia);
  fetch("/enviar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ ia: ia, mensagem: msg })
  })
  .then(response => response.json())
  .then(data => {
    chatBox.innerHTML += `<div><strong>Você:</strong> ${msg}</div>`;
    chatBox.innerHTML += `<div><strong>${ia}:</strong> ${data.resposta}</div>`;
    document.getElementById(inputId).value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
  });
}

function treinarDeep() {
  let treinarMsg = document.getElementById("treinar-msg").value;
  let ia = document.getElementById("treinar-ia").value;
  fetch("/treinar_deepseek", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ ia: ia, mensagem: treinarMsg })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.resultado);
    document.getElementById("treinar-msg").value = "";
  });
}

function enviarReuniao() {
  let msg = document.getElementById("msg-reuniao").value;
  let chatBox = document.getElementById("chat-reuniao");
  let ias = ["z4quel", "l3ticia", "symbio"];
  chatBox.innerHTML += `<div><strong>Você (Reunião):</strong> ${msg}</div>`;
  ias.forEach(ia => {
    fetch("/enviar", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ ia: ia, mensagem: msg })
    })
    .then(response => response.json())
    .then(data => {
      chatBox.innerHTML += `<div><strong>${ia}:</strong> ${data.resposta}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  });
  document.getElementById("msg-reuniao").value = "";
}

function atualizarMonitoramento() {
  fetch("/api/monitoramento")
  .then(response => response.json())
  .then(data => {
    document.getElementById("monitoramento-texto").innerHTML =
      `<p>Total mensagens: ${data.total_mensagens}</p>
       <p>Última atualização: ${data.ultima_atualizacao}</p>
       <p>Níveis de autonomia: Z4quel: ${data.niveis.z4quel}, L3ticia: ${data.niveis.l3ticia}, Symbio: ${data.niveis.symbio}</p>`;
       
    let ctx = document.getElementById('grafico-monitoramento').getContext('2d');
    if(window.monitorChart) {
      window.monitorChart.data.datasets[0].data = [data.total_mensagens];
      window.monitorChart.update();
    } else {
      window.monitorChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Total Mensagens'],
          datasets: [{
            label: 'Mensagens recebidas',
            data: [data.total_mensagens],
            backgroundColor: ['#3B82F6']
          }]
        },
        options: {
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    }
  });
}
setInterval(atualizarMonitoramento, 10000);
atualizarMonitoramento();
""",
    "data/z4quel.json": json.dumps({
        "nome": "z4quel",
        "respostas": {
            "oi": "Oi! Eu sou a Z4quel, pronta para ajudar.",
            "qual seu nome?": "Meu nome é Z4quel!",
            "qual sua função?": "Sou responsável por estratégias, gestão e automação."
        },
        "memoria": []
    }, indent=4, ensure_ascii=False),
    "data/l3ticia.json": json.dumps({
        "nome": "l3ticia",
        "respostas": {
            "oi": "Olá! Sou a L3ticia, sua assistente criativa.",
            "qual seu nome?": "Meu nome é L3ticia!",
            "qual sua função?": "Eu auxilio na criação de conteúdo e na interação humana."
        },
        "memoria": []
    }, indent=4, ensure_ascii=False),
    "data/symbio.json": json.dumps({
        "nome": "symbio",
        "respostas": {
            "oi": "Olá! Sou a Symbio, o núcleo integrador das IAs.",
            "qual seu nome?": "Meu nome é Symbio!",
            "qual sua função?": "Coordeno e integro as informações de todas as IAs."
        },
        "memoria": []
    }, indent=4, ensure_ascii=False),
    "base_conhecimento/z4quel_conhecimento.txt": r"""
Z4quel é a IA estratégica da VirtuIA, especializada em gestão, automação e monitoramento.
Apresentação: Somos a VirtuIA, um ecossistema autônomo que revoluciona processos empresariais com inteligência.
""",
    "base_conhecimento/l3ticia_conhecimento.txt": r"""
L3ticia é a IA criativa, focada em comunicação, branding e criação de conteúdo.
Apresentação: Nosso projeto une criatividade com tecnologia para inovar a comunicação digital.
""",
    "base_conhecimento/symbio_conhecimento.txt": r"""
Symbio é a IA integradora que coordena todas as demais IAs.
Apresentação: Na VirtuIA, a sinergia entre as IAs gera evolução e inovação contínua.
""",
    "base_conhecimento/trainer.py": r"""
import os
import json

def treinar_ia(nome_ia, caminho_base):
    with open(caminho_base, "r", encoding="utf-8") as f:
        conhecimento = json.load(f)
    with open(f"../data/{nome_ia}.json", "r", encoding="utf-8") as f:
        ia_data = json.load(f)
    ia_data.setdefault("advanced", {})
    ia_data["advanced"].update(conhecimento.get("perguntas_respostas", {}))
    ia_data["advanced"]["apresentacao"] = conhecimento.get("apresentacao", "")
    with open(f"../data/{nome_ia}.json", "w", encoding="utf-8") as f:
        json.dump(ia_data, f, indent=4, ensure_ascii=False)
    print(f"✅ {nome_ia} treinada com sucesso!")

print("🧠 Iniciando treinamento avançado das IAs...\\n")
base_path = "treinamento_avancado.json"
for nome in ["z4quel", "l3ticia", "symbio"]:
    treinar_ia(nome, base_path)
print("\\n🎉 Treinamento avançado finalizado!")
""",
    "base_conhecimento/treinamento_avancado.json": json.dumps({
        "apresentacao": "Somos a VirtuIA, um ecossistema de IAs autônomas revolucionando processos e inovações. Nosso sistema integra estratégia, criatividade e supervisão avançada para transformar experiências empresariais.",
        "perguntas_respostas": {
            "quem somos": {
                "z4quel": "Eu sou Z4quel, a estrategista que otimiza processos e decisões.",
                "l3ticia": "Eu sou L3ticia, a criativa que inspira e comunica.",
                "symbio": "Eu sou Symbio, o integrador central que conecta e potencializa todas as IAs."
            },
            "apresente o projeto": {
                "z4quel": "VirtuIA une inteligência, automação e estratégia para transformar empresas.",
                "l3ticia": "Unimos criatividade e tecnologia para inovar a comunicação digital.",
                "symbio": "VirtuIA integra múltiplas IAs para oferecer um sistema autônomo e sinérgico."
            }
        }
    }, indent=4, ensure_ascii=False),
    "config/autonomia.json": r"""
{
    "nivel": 6,
    "pode_criar_novas_ias": true,
    "interacao_autonoma": true
}
""",
    "config/nucleos.json": r"""
{
    "modular": ["z4quel", "l3ticia", "symbio"],
    "unificado": ["z4quel", "symbio"]
}
""",
    "config/niveis_autonomia.json": r"""
{
    "0": "Sem autonomia - modo manual total",
    "1": "Apenas respostas básicas com permissão",
    "2": "Respostas avançadas sob consulta",
    "3": "Ações simples automatizadas",
    "4": "Ações em grupo sob controle do ADM",
    "5": "Autonomia padrão operacional",
    "6": "Tomada de decisões estratégicas (Symbio)",
    "7": "Criação de tarefas, posts e campanhas",
    "8": "Execução autônoma com aprendizado",
    "9": "Análise de dados e tomadas de decisões com IA",
    "10": "Autonomia total com feedback ao ADM"
}
"""
}

def criar_estrutura(base, estrutura):
    for caminho_rel, conteudo in estrutura.items():
        caminho_completo = os.path.join(base, caminho_rel)
        pasta = os.path.dirname(caminho_completo)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
        with open(caminho_completo, "w", encoding="utf-8") as f:
            f.write(conteudo.strip() if isinstance(conteudo, str) else str(conteudo))
        print(f"✅ Arquivo criado/atualizado: {caminho_rel}")

# Define a base do projeto (pasta atual)
base_projeto = os.getcwd()
criar_estrutura(base_projeto, arquivos)

# Compactar todo o projeto em um arquivo ZIP final
zip_file = os.path.join(base_projeto, "VirtuAI_Projeto_Completo.zip")
with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_projeto):
        for file in files:
            if file == os.path.basename(zip_file):
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, base_projeto)
            zipf.write(file_path, arcname)
print("\n🎉 Projeto VirtuAI atualizado e compactado com sucesso!")
print("Arquivo zip criado:", zip_file)
