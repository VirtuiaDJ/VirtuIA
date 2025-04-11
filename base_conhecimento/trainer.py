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