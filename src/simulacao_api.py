import requests
import time
import random
from datetime import datetime
import os, json


# Configurações do Limiar baseadas no código C++ do ESP32
LIMIAR_FUMACA = 400

def gerar_dados_sensores():
    """
    Gera dados simulados para o DHT22 e MQ-2.
    Garante uma chance matemática exata de 20% de gerar um cenário de risco.
    """
    # random.random() gera um número flutuante entre 0.0 e 1.0
    # Se o número for menor ou igual a 0.20, temos a probabilidade de 20% selecionada
    e_cenario_de_risco = random.random() <= 0.20
    
    if e_cenario_de_risco:
        # Cenário de Risco (Incêndio detectado na floresta)
        temperatura = round(random.uniform(38.0, 48.0), 1)  # Altas temperaturas
        humidade = round(random.uniform(5.0, 15.0), 1)       # Ar extremamente seco
        nivel_fumaca = random.randint(450, 850)              # Acima do limiar de 400
        alerta_local = True
        status_log = "🚨 [RISCO DETECTADO]"
    else:
        # Cenário Normal (Condições climáticas estáveis)
        temperatura = round(random.uniform(22.0, 32.0), 1)  # Temperaturas normais
        humidade = round(random.uniform(40.0, 70.0), 1)     # Humidade saudável
        nivel_fumaca = random.randint(120, 320)              # Abaixo do limiar de 400
        alerta_local = False
        status_log = "🟢 [NORMAL]"

    # Monta o payload JSON idêntico ao que o ESP32 real/Wokwi envia
    payload = {
        "temperatura": temperatura,
        "humidade": humidade,
        "nivel_fumaca": nivel_fumaca,
        "alerta_local": alerta_local
    }

   ## --- PARTE NOVA: MANIPULAÇÃO DO HISTÓRICO JSON ---
    caminho_diretorio = "C:/Users/davih/OneDrive/Documentos/PROJETOS/Fiap/ANO 2/Global Solutions 1/data"
    caminho_arquivo = os.path.join(caminho_diretorio, "historico_telemetria.json")
    
    # Garante que a estrutura de pastas da FIAP exista
    os.makedirs(caminho_diretorio, exist_ok=True)
    
    historico = []
    
    # Se o arquivo já existir, abre e carrega a lista existente
    if os.path.exists(caminho_arquivo):
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                historico = json.load(f)
                # Garante que o conteúdo seja uma lista
                if not isinstance(historico, list):
                    historico = []
        except json.JSONDecodeError:
            # Se o arquivo estiver corrompido ou vazio, reinicia a lista
            historico = []

    # Adiciona o novo payload gerado ao fim do histórico
    historico.append(payload)
    
    # Salva novamente o arquivo com os dados atualizados
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
        
    print(f"💾 Dado salvo no histórico local ({caminho_arquivo})")
    
    return payload, status_log

def rodar_simulador():
    print("==========================================================")
    print("🛰️  SatGuard-Edge — Script de Simulação de Solo (ESP32)  🛰️")
    print("Frequência de atualização: 1 em 1 minuto (60 segundos)")
    print("Probabilidade de Risco configurada: 20%")
    print("==========================================================")
    
    while True:
        # 1. Gera os dados na borda simulada
        dados, status = gerar_dados_sensores()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n[{timestamp}] Gerando dados de telemetria... Tipo: {status}")
        print(f"-> Temp: {dados['temperatura']}°C | Hum: {dados['humidade']}% | Fumaça: {dados['nivel_fumaca']}")
            
        # 2. Aguarda exatamente 1 minuto (60 segundos) antes da próxima leitura
        print("⏱️  Aguardando 60 segundos para a próxima varredura de solo...")
        time.sleep(60)

if __name__ == "__main__":
    rodar_simulador()