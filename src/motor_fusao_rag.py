import os
import json
import numpy as np
from google import genai
from sentence_transformers import SentenceTransformer

# 1. Configura a API do Gemini (Certifique-se de ter a variável de ambiente GEMINI_API_KEY configurada)
# Caso queira testar direto, pode passar o token de forma explícita: client = genai.Client(api_key="SUA_CHAVE")
client = genai.Client()

# Carrega um modelo de embeddings leve que roda 100% local e de graça na sua máquina
print("🧠 Carregando modelo de embeddings local...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def carregar_e_fatiar_manual():
    """Lê o manual de contingência e separa em blocos para busca vetorial."""
    caminho = "data/processed/manual_contingencia.txt"
    if not os.path.exists(caminho):
        return ["Diretriz padrão: Acione a Defesa Civil imediatamente em caso de fogo."]
    
    with open(caminho, "r", encoding="utf-8") as f:
        texto = f.read()
    
    # Separa o texto por parágrafos/diretrizes
    blocos = [bloco.strip() for bloco in texto.split("\n\n") if bloco.strip()]
    return blocos

def buscar_contexto_relevante(query, blocos, top_k=1):
    """Transforma os textos em vetores matemáticos e faz a busca por proximidade."""
    # Gera o vetor da pergunta
    vetor_query = encoder.encode(query)
    # Gera os vetores de todos os blocos do manual
    vetores_blocos = encoder.encode(blocos)
    
    # Calcula a similaridade de cosseno (distância matemática entre os vetores)
    similaridades = np.dot(vetores_blocos, vetor_query) / (np.linalg.norm(vetores_blocos, axis=1) * np.linalg.norm(vetor_query))
    
    # Pega o índice do bloco mais parecido
    melhor_indice = np.argmax(similaridades)
    return blocos[melhor_indice]

def executar_fusao_e_rag(status_satelite: bool, confianca_satelite: float, dados_esp32: dict, dados_clima: dict):
    """
    MOTOR DE FUSÃO DE DADOS: Cruza as 3 fontes de informação 
    e usa o RAG para gerar o plano de ação ideal.
    """
    print("\n🎛️ [FUSÃO DE DADOS] Iniciando correlação de fontes...")
    
    # Lógica de correlação/fusão de dados do ecossistema
    alerta_confirmado = False
    if status_satelite and dados_esp32.get("alerta_local", False):
        alerta_confirmado = True
        print("⚠️ [ALERTA MÁXIMO] Fusão detectou congruência espacial! Satélite e Solo confirmam o incêndio.")
    elif status_satelite:
        print("🔍 [ALERTA MODERADO] Apenas o satélite indica anomalia. Verificando dados terrestres...")
        
    # Constrói o cenário atual baseado na fusão
    contexto_cenario = f"""
    Cenário Atual Detectado pelo Sistema:
    - Foco por Satélite (YOLO): {'Sim' if status_satelite else 'Não'} (Confiança: {confianca_satelite}%)
    - Sensor Terrestre (ESP32): Temperatura {dados_esp32.get('temperatura')}°C, Fumaça {dados_esp32.get('nivel_fumaca')}
    - Dados de Automação Web (Vento): {dados_clima.get('velocidade_vento_kmh')} km/h
    - Umidade do Ar: {dados_clima.get('umidade_relativa_ar_porcentagem')}%
    """
    
    # --- ETAPA RAG: Busca a diretriz correta no manual baseado no cenário ---
    blocos_manual = carregar_e_fatiar_manual()
    diretriz_recuperada = buscar_contexto_relevante(contexto_cenario, blocos_manual)
    
    # --- ETAPA GENERATIVA: Envia o cenário + diretriz do manual para a LLM formatar ---
    prompt_final = f"""
    Você é a Inteligência Artificial do painel orbital SatGuard-Edge.
    Sua tarefa é ler os dados da Fusão de Sensores e aplicar RIGOROSAMENTE a Diretriz do Manual fornecida.
    
    {contexto_cenario}
    
    Diretriz Oficial do Manual Recuperada via RAG:
    {diretriz_recuperada}
    
    Gere um relatório de ação curto, técnico e urgente para os operadores da sala de controle, contendo:
    1. Diagnóstico do Risco de Alastramento
    2. Plano de Ação Imediato baseado na Diretriz
    3. Contatos de Emergência citados na Diretriz
    """
    
    print("🤖 [LLM / RAG] Solicitando geração do relatório à Inteligência Artificial...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_final,
        )
        
        relatorio_gerado = response.text
        print("\n================== RELATÓRIO DE CONTINGÊNCIA GERADO ==================")
        print(relatorio_gerado)
        print("=======================================================================")
        
        # Salva o resultado final para o dashboard da Lais ler depois
        with open(r"C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\data\relatorio_final_operacao.txt", "w", encoding="utf-8") as f:
            f.write(relatorio_gerado)
            
        return relatorio_gerado
    except Exception as e:
        print(f"❌ Erro ao chamar a API Generativa: {str(e)}")
        return None

# # --- Simulação de Teste de Integração de Todo o Sistema ---
# if __name__ == "__main__":
#     # 1. Dados simulados vindos da Visão Computacional (Fase 3 do Davi)
#     yolo_fogo = True
#     yolo_conf = 85.5
    
#     # 2. Dados simulados vindos do ESP32 via API (Fase 2 da Lais)
#     json_esp32 = {"temperatura": 42.5, "humidade": 12.0, "nivel_fumaca": 650, "alerta_local": True}
    
#     # 3. Dados simulados vindos do Web Scraper (Fase 4 do Lucas)
#     json_clima = {"velocidade_vento_kmh": 26.4, "umidade_relativa_ar_porcentagem": 15}
    
#     # Executa a integração ponta a ponta
#     executar_fusao_e_rag(yolo_fogo, yolo_conf, json_esp32, json_clima)