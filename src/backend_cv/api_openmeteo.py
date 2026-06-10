import requests
import json
import os
from datetime import datetime

def coletar_dados_climaticos_regiao(latitude: float, longitude: float):
    """
    Simula um robô de automação que busca dados de vento e umidade em tempo real 
    para alimentar a inteligência do projeto SatGuard-Edge.
    Utiliza a API pública Open-Meteo (não exige chave/token de acesso).
    """
    print(f"🌐 [AUTOMAÇÃO] Acessando dados meteorológicos para as coordenadas: Lat {latitude}, Lon {longitude}...")
    
    # URL da API pública de meteorologia
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    
    try:
        # Dispara a requisição HTTP GET para o servidor externo
        resposta = requests.get(url, timeout=10)
        
        # Se a requisição for bem-sucedida (Status 200)
        if resposta.status_code == 200:
            dados_brutos = resposta.json()
            
            # Extrai os dados específicos do bloco 'current' (atual)
            dados_atuais = dados_brutos.get("current", {})
            
            umidade = dados_atuais.get("relative_humidity_2m")
            velocidade_vento = dados_atuais.get("wind_speed_10m")
            temperatura_ar = dados_atuais.get("temperature_2m")
            
            # Estrutura o resultado que será injetado no RAG do Davi
            relatorio_climatico = {
                "timestamp_coleta": datetime.now().isoformat(),
                "coordenadas": {"lat": latitude, "lon": longitude},
                "temperatura_ar_celcius": temperatura_ar,
                "umidade_relativa_ar_porcentagem": umidade,
                "velocidade_vento_kmh": velocidade_vento,
                "fator_risco_espalhamento": "ALTO" if velocidade_vento > 20.0 or umidade < 30 else "MODERADO"
            }
            
            print("✅ [AUTOMAÇÃO] Dados externos capturados com sucesso!")
            print(f"-> Vento: {velocidade_vento} km/h | Umidade do Ar: {umidade}%")
            print(f"-> Fator de Risco Calculado: {relatorio_climatico['fator_risco_espalhamento']}")
            
            # Salva o arquivo JSON de dados na pasta data/processed para deixar o histórico limpo
            pasta_destino = "data/processed/"
            os.makedirs(pasta_destino, exist_ok=True)
            caminho_arquivo = os.path.join(pasta_destino, "clima_regiao_monitorada.json")
            
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(relatorio_climatico, f, indent=4, ensure_ascii=False)
                
            print(f"[AUTOMAÇÃO] Log de ingestão salvo em: {caminho_arquivo}")
            return relatorio_climatico
            
        else:
            print(f"❌ [ERRO AUTOMAÇÃO] Falha na resposta do servidor externo. Status: {resposta.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ [ERRO AUTOMAÇÃO] Falha crítica ao rodar o scraper: {str(e)}")
        return None

if __name__ == "__main__":
    # Teste de execução isolado do script do Lucas
    # Coordenadas aproximadas do coração da Amazônia (-3.46, -62.21)
    coletar_dados_climaticos_regiao(latitude=-3.46, longitude=-62.21)