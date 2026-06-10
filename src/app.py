import json, os, random, pandas as pd, streamlit as st, plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from backend_cv.simulacao_api import gerar_dados_sensores
from backend_cv.api_openmeteo import coletar_dados_climaticos_regiao
from backend_cv.satelite import executar_teste_local
from motor_fusao_rag import executar_fusao_e_rag

# Configuração da página do Streamlit (Modo Escuro/Visual Espacial)
st.set_page_config(
    page_title="SatGuard-Edge | Dashboard",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

count = st_autorefresh(interval=60000, key="dashboard_refresh")

# Estilização em CSS para dar cara de "Painel Militar/Espacial"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { !important; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { background-color: #00ffcc; color: black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Título Principal do Dashboard
st.title("🛰️ SatGuard-Edge — Monitoramento Orbital e Terrestre")
st.subheader("Global Solutions 2026.1 — Engenharia de IA FIAP")

# Sidebar com informações do Grupo
st.sidebar.title("Navegação e Equipe")
st.sidebar.markdown("""
**Integrantes:**
- Davi Ferreira
- Lais Kurahashi
- Lucas Martinelli

**Status do Sistema:** 🟢 ONLINE
""")

# Criação das Abas de Navegação
tab_comando, tab_rag = st.tabs(["🛸 Centro de Comando Orbital", "📋 Relatório de Contingência (RAG)"])

# --- ABA 1: CENTRO DE COMANDO ORBITAL ---
with tab_comando:
    dados_esp32 = gerar_dados_sensores()    

    st.header("Monitoramento de Sensores e Imagens Satelitais")
    
    # Grid Superior: 3 Cartões de Status (Métricas em Tempo Real)
    col1, col2, col3 = st.columns(3)
    
    # Simulação de dados do ESP32 da Lais
    temp_simulada = dados_esp32[0]['temperatura']
    fumaca_simulada = dados_esp32[0]['nivel_fumaca']
    alerta_solo = "🚨 CRÍTICO" if fumaca_simulada > 400 else "🟢 NORMAL"
    
    with col1:
        st.metric(label="🌡️ Temperatura em Solo (ESP32)", value=f"{temp_simulada} °C", delta="Mapeamento Local")
    with col2:
        st.metric(label="💨 Índice de Fumaça (MQ-2)", value=fumaca_simulada, delta=alerta_solo, delta_color="inverse" if fumaca_simulada > 400 else "normal")
    with col3:
        # Puxa o arquivo JSON que o robô do Lucas gerou na Fase 4
        caminho_clima = "data/processed/clima_regiao_monitorada.json"
        try:
            clima = coletar_dados_climaticos_regiao(latitude=-3.46, longitude=-62.21)
            st.metric(label="💨 Velocidade do Vento (Scraper Web)", value=f"{clima['velocidade_vento_kmh']} km/h", delta=f"Umidade: {clima['umidade_relativa_ar_porcentagem']}%")
        except:
            st.metric(label="💨 Velocidade do Vento (Scraper Web)", value="24.5 km/h", delta="Umidade: 18% (Simulado)")

    st.markdown("---")

    # Divisão da Tela: Esquerda (Visão do Satélite), Direita (Gráficos de Telemetria)
    col_esquerda, col_direita = st.columns([1, 1])
    
    with col_esquerda:
        caminho_imagens_satelite = r'C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\data\YoLo_Dataset\YOLO_datasets\valid\images'
        st.subheader("📷 Varredura de Imagem Satelital (YOLOv8)")
        
        # Simulação do Satélite escolhendo a imagem da pasta data/raw
        opcao_imagem = st.selectbox(
            "Selecione o frame capturado pelo Satélite para análise:",
            [i for i in os.listdir(caminho_imagens_satelite)]
        )
        
        btn_analisar = st.button("Executar Varredura Orbital")
        
        if btn_analisar:
            st.info("🔄 Rodando inferência de rede neural na GPU...")
            
            # Aqui simulamos a exibição da imagem processada pelo Davi (salva na pasta processed)
            # Para o teste, garanta que exista uma imagem nessa pasta ou coloque um placeholder
            caminho_anotada = f'{caminho_imagens_satelite}/{opcao_imagem}'
            caminho_imagem_processada = r'C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\data\processed'
            yolo = executar_teste_local(caminho_anotada, caminho_imagem_processada)

            if os.path.exists(caminho_imagem_processada):
                st.image(f'{caminho_imagem_processada}/resultado_teste_local.jpg', caption=f"Análise Concluída — {opcao_imagem}", use_column_width=True)
                st.success("🎯 Varredura orbital concluída com sucesso!")
            else:
                st.error("Erro: A imagem processada não foi gerada na pasta 'data/processed/'. Check o script de teste local.")

        
    with col_direita:
        df_dados_salvos = pd.read_json(r'C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\data\historico_telemetria.json')
        st.subheader("📈 Histórico de Telemetria Espacial (IoT)")
        
        # Criação de um gráfico dinâmico usando Plotly para simular o histórico dos sensores da Lais
        dados_grafico = {
            "Horário": df_dados_salvos['data_hora'].values.tolist(),
            "Temperatura (°C)": df_dados_salvos['temperatura'].values.tolist(),
            "Nível de Fumaça": df_dados_salvos['nivel_fumaca'].values.tolist()
        }
        df = pd.DataFrame(dados_grafico)
        
        fig_temp = px.line(df, x="Horário", y="Temperatura (°C)", title="Evolução Térmica do Solo", markers=True)
        fig_temp.update_traces(line_color="#ff5555")
        st.plotly_chart(fig_temp, use_container_width=True)
        
        fig_smoke = px.bar(df, x="Horário", y="Nível de Fumaça", title="Concentração de Partículas de Carbono (MQ-2)", color="Nível de Fumaça", color_continuous_scale="Reds")
        st.plotly_chart(fig_smoke, use_container_width=True)

# --- ABA 2: RELATÓRIO DE CONTINGÊNCIA (RAG) ---
with tab_rag:
    st.header("🧠 Inteligência Generativa e Recuperação de Manuais (RAG)")
    st.markdown("Abaixo é apresentado o relatório gerado pela LLM após correlacionar as métricas de solo, vento e a detecção de satélite com as diretrizes do IBAMA/INPE.")
    
    btn_gerar_rag = st.button("Gerar Relatório de Missão via RAG")
    
    if btn_gerar_rag:
        # Verifica se o Davi rodou a análise do satélite na Aba 1 primeiro
        if 'yolo' in locals() or ('clima' in locals() and clima is not None):
            st.info("🔍 Consultando base de dados vetorial e acionando inteligência generativa...")
            
            # Captura os dados de segurança caso a varredura orbital não tenha sido clicada ainda
            status_satelite = yolo[0] if 'yolo' in locals() else False
            confianca_satelite = yolo[1] if 'yolo' in locals() else 0.0
            
            # ✅ Executa a fusão e o RAG APENAS quando o usuário clica no botão
            executar_fusao_e_rag(
                status_satelite, 
                confianca_satelite, 
                dados_esp32[0], # Passa o dicionário correto gerado pelo simulador
                clima # Passa o dicionário completo do clima do Lucas
            )
        else:
            # Fallback seguro caso o usuário clique direto na aba 2 ao abrir o sistema
            st.warning("🔄 Processando dados em lote para geração do relatório...")
            try:
                clima_atual = coletar_dados_climaticos_regiao(latitude=-3.46, longitude=-62.21)
                executar_fusao_e_rag(False, 0.0, dados_esp32[0], clima_atual)
            except:
                clima_ficticio = {"velocidade_vento_kmh": 24.5, "umidade_relativa_ar_porcentagem": 18}
                executar_fusao_e_rag(False, 0.0, dados_esp32[0], clima_ficticio)

        # Puxa o relatório gerado pelo script da Fase 5
        caminho_relatorio = r"C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\data\relatorio_final_operacao.txt"
        
        if os.path.exists(caminho_relatorio):
            with open(caminho_relatorio, "r", encoding="utf-8") as f:
                conteudo_relatorio = f.read()
            
            st.markdown("### 📝 Relatório Oficial Emitido")
            st.text_area(label="Consola de Saída da LLM", value=conteudo_relatorio, height=400)
            st.download_button(label="📥 Baixar Relatório Técnico (.txt)", data=conteudo_relatorio, file_name="Relatorio_SatGuard_Edge.txt")
        else:
            st.error("Nenhum relatório encontrado! Verifique a pasta 'data/'.")