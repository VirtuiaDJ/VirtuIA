#!/bin/bash
# ==============================================================================
# SCRIPT COMPLETO DE INSTALAÇÃO E ATUALIZAÇÃO DO VIRTUAI
# ==============================================================================
# Por: Z4quel & Izael Brito ✊🧠
# Data: 2025-04-11
# Versão: 1.0 FINAL
# ------------------------------------------------------------------------------

PROJETO="VirtuAI"
DIR="/opt/$PROJETO"
VENV="$DIR/venv"
LOGFILE="/var/log/$PROJETO.log"

echo "================== 🚀 INICIANDO INSTALAÇÃO COMPLETA DO $PROJETO =================="

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOGFILE"
}

# Instalar pacotes do sistema
log "🔧 Instalando dependências do sistema..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Criar diretório do projeto
log "📁 Criando estrutura de diretórios..."
sudo mkdir -p "$DIR"/{templates,static/css,static/js,data,base_conhecimento,config}
cd "$DIR"

# Criar ambiente virtual
log "📦 Criando ambiente virtual..."
python3 -m venv "$VENV"
source "$VENV/bin/activate"

# Criar requirements.txt
log "📝 Gerando requirements.txt..."
cat <<EOF > requirements.txt
flask
apscheduler
matplotlib
psutil
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivos principais
log "🧠 Criando app.py..."
cat <<EOF > app.py
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monitoramento')
def monitoramento():
    return render_template('monitoramento.html')

@app.route('/sala')
def sala_reuniao():
    return render_template('sala_reuniao.html')

@app.route('/treinamento')
def treinamento():
    return render_template('treinamento.html')

@app.route('/autonomia', methods=['GET', 'POST'])
def alterar_autonomia():
    path = "config/autonomia.json"
    if request.method == 'POST':
        dados = request.json
        with open(path, 'w') as f:
            json.dump(dados, f)
        return jsonify({"status": "autonomia atualizada"})
    else:
        with open(path) as f:
            return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True)
EOF

# Criar templates HTML
log "📄 Criando templates..."
cat <<EOF > templates/index.html
<h1>VirtuAI - Interface Principal</h1>
<a href="/monitoramento">Monitoramento</a> |
<a href="/sala">Sala de Reunião</a> |
<a href="/treinamento">Treinamento</a>
EOF

echo "<h1>Monitoramento do Sistema</h1>" > templates/monitoramento.html
echo "<h1>Sala de Reunião Virtual</h1>" > templates/sala_reuniao.html
echo "<h1>Área de Treinamento</h1>" > templates/treinamento.html

# CSS e JS básicos
echo "body { font-family: sans-serif; background: #f9f9f9; }" > static/css/style.css
echo "console.log('VirtuAI JS Loaded');" > static/js/script.js

# Criar arquivos de dados
log "🧬 Criando arquivos de dados e conhecimento..."
cat <<EOF > config/autonomia.json
{
  "z4quel": 5,
  "l3ticia": 5,
  "symbio": 6
}
EOF

touch data/z4quel.json data/l3ticia.json data/symbio.json
touch base_conhecimento/z4quel_conhecimento.txt
touch base_conhecimento/l3ticia_conhecimento.txt
touch base_conhecimento/symbio_conhecimento.txt
touch base_conhecimento/treinamento_avancado.json

# Criar trainer.py (placeholder)
cat <<EOF > base_conhecimento/trainer.py
# Placeholder para treinamento das IAs
print("Treinamento iniciado...")
EOF

# Criar atualizador.py
cat <<EOF > atualizador.py
import os
import subprocess

print("🔄 Atualizando VirtuAI...")
os.system("git pull origin main")
subprocess.call(["pip", "install", "-r", "requirements.txt"])
EOF

# Criar serviço do Gunicorn
log "⚙️ Criando serviço Gunicorn para Flask..."
sudo tee "/etc/systemd/system/$PROJETO.service" > /dev/null <<EOF
[Unit]
Description=Gunicorn do $PROJETO
After=network.target

[Service]
User=$USER
WorkingDirectory=$DIR
Environment="PATH=$VENV/bin"
ExecStart=$VENV/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $PROJETO
sudo systemctl restart $PROJETO

# NGINX config
log "🌐 Configurando NGINX..."
sudo tee /etc/nginx/sites-available/$PROJETO > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/$PROJETO /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

log "✅ VirtuAI instalado com sucesso em: http://localhost"
echo -e "\n⚠️ Lembre de apontar seu domínio ou IP para o servidor!\n"
