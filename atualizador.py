import os
import subprocess
import json
import shutil

# Função para garantir que o diretório exista
def criar_diretorio(diretorio):
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
        print(f"Diretório {diretorio} criado com sucesso.")
    else:
        print(f"Diretório {diretorio} já existe.")

# Função para verificar a instalação das dependências
def instalar_dependencias():
    try:
        subprocess.check_call([os.sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar as dependências: {e}")
        exit(1)

# Função para atualizar arquivos de configuração e base de conhecimento
def atualizar_arquivos():
    # Criação dos arquivos de dados e base de conhecimento
    data_dir = "data"
    criar_diretorio(data_dir)
    arquivos_data = ['z4quel.json', 'l3ticia.json', 'symbio.json']
    for arquivo in arquivos_data:
        caminho_arquivo = os.path.join(data_dir, arquivo)
        if not os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'w') as f:
                json.dump({}, f)  # Arquivo JSON vazio para começar
            print(f"Arquivo {arquivo} criado em {data_dir}.")
        else:
            print(f"Arquivo {arquivo} já existe em {data_dir}.")
    
    base_conhecimento_dir = "base_conhecimento"
    criar_diretorio(base_conhecimento_dir)
    arquivos_base_conhecimento = ['z4quel_conhecimento.txt', 'l3ticia_conhecimento.txt', 'symbio_conhecimento.txt']
    for arquivo in arquivos_base_conhecimento:
        caminho_arquivo = os.path.join(base_conhecimento_dir, arquivo)
        if not os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'w') as f:
                f.write("")  # Arquivo de conhecimento vazio
            print(f"Arquivo {arquivo} criado em {base_conhecimento_dir}.")
        else:
            print(f"Arquivo {arquivo} já existe em {base_conhecimento_dir}.")

    # Atualizar o arquivo de configuração autonomia.json
    config_dir = "config"
    criar_diretorio(config_dir)
    autonomia_path = os.path.join(config_dir, "autonomia.json")
    if not os.path.exists(autonomia_path):
        autonomia_data = {
            "z4quel": 5,
            "l3ticia": 5,
            "symbio": 6
        }
        with open(autonomia_path, 'w') as f:
            json.dump(autonomia_data, f)
        print(f"Arquivo autonomia.json criado em {config_dir}.")
    else:
        print("Arquivo autonomia.json já existe em config.")

# Função para criar a estrutura de templates e estáticos
def criar_estrutura_html():
    templates_dir = "templates"
    criar_diretorio(templates_dir)

    templates = {
        "index.html": "<html><body><h1>Bem-vindo ao VirtuAI</h1></body></html>",
        "monitoramento.html": "<html><body><h1>Painel de Monitoramento</h1></body></html>",
        "sala_reuniao.html": "<html><body><h1>Sala de Reunião Virtual</h1></body></html>",
        "treinamento.html": "<html><body><h1>Treinamento IA</h1></body></html>"
    }
    
    for template, conteudo in templates.items():
        caminho_template = os.path.join(templates_dir, template)
        if not os.path.exists(caminho_template):
            with open(caminho_template, 'w') as f:
                f.write(conteudo)
            print(f"Template {template} criado em {templates_dir}.")
        else:
            print(f"Template {template} já existe em {templates_dir}.")

    # Criando diretórios para arquivos estáticos
    static_dir = "static"
    css_dir = os.path.join(static_dir, "css")
    js_dir = os.path.join(static_dir, "js")
    criar_diretorio(css_dir)
    criar_diretorio(js_dir)

    # Arquivos estáticos (CSS e JS)
    style_path = os.path.join(css_dir, "style.css")
    if not os.path.exists(style_path):
        with open(style_path, 'w') as f:
            f.write("body { font-family: Arial, sans-serif; background-color: #f4f4f9; }")
        print("Arquivo style.css criado em static/css.")
    
    script_path = os.path.join(js_dir, "script.js")
    if not os.path.exists(script_path):
        with open(script_path, 'w') as f:
            f.write("// Seu script JS aqui")
        print("Arquivo script.js criado em static/js.")

# Função principal para rodar o atualizador
def rodar_atualizador():
    print("Iniciando o atualizador...")

    # Verificar e criar diretórios necessários
    criar_diretorio("VirtuAI")
    criar_diretorio("config")
    criar_diretorio("base_conhecimento")
    criar_diretorio("data")
    criar_diretorio("static")
    criar_diretorio("templates")
    
    # Instalar dependências
    instalar_dependencias()

    # Atualizar arquivos essenciais
    atualizar_arquivos()

    # Criar estrutura de HTML e arquivos estáticos
    criar_estrutura_html()

    print("Atualização concluída com sucesso!")

if __name__ == "__main__":
    rodar_atualizador()
