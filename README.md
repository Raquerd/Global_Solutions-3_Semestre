


# 🛰️ SatGuard-Edge — Monitoramento Inteligente de Desastres Ambientais

## 📋 Sobre o Projeto
O **SatGuard-Edge** é uma Prova de Conceito (POC) de arquitetura distribuída desenvolvida para a **Global Solutions 2026.1** da FIAP. O objetivo principal do ecossistema é mitigar o impacto de incêndios florestais correlacionando o monitoramento macroscópico orbital (via satélite) com a validação microscópica em tempo real em solo (via IoT). 

Para orquestrar a tomada de decisão sem falsos alarmes ou alucinações, um pipeline de Inteligência Artificial Generativa baseado em **RAG (Retrieval-Augmented Generation)** consome a fusão dessas informações e gera relatórios técnicos e planos de ação automáticos baseados em manuais de contingência oficiais do IBAMA e INPE.

O projeto divide-se em 4 camadas totalmente integradas:
1.  **Borda Terrestre (IoT):** Microcontrolador ESP32 conectado a sensores DHT22 e MQ-2 para medir temperatura, umidade e fumaça em solo.
2.  **Visão Computacional (Orbital):** Modelo local YOLOv8 que processa imagens de satélite para detecção de focos de fogo/fumaça.
3.  **Automação Web (Ingestão Externa):** Web scraper que consome dados meteorológicos em tempo real (Open-Meteo API) para obter a velocidade do vento regional.
4.  **Camada Generativa (RAG) & Painel:** Motor que cruza os dados obtidos, busca a diretriz correta em um arquivo vetorial local e aciona a LLM do Gemini para gerar o relatório final exposto em um painel Streamlit.

---

## 🧠 Aprendizados Aplicados (Fases 3 e 4 da FIAP)
O projeto materializa conceitos avançados ministrados ao longo do ano letivo:

* **Visão Computacional Local e Otimização:** Aprendemos a carregar pesos customizados (`best.pt`) fora do ambiente de nuvem do Google Colab, tratando tensores diretamente no hardware local via PyTorch, extraindo chaves de confiança (`r.boxes.conf`) e condicionais booleanas de detecção.
* **Manipulação de Dados e Históricos com Pandas:** Aplicação prática de engenharia de dados ao ler arquivos em streaming (JSON) e convertê-los em DataFrames estruturados (`pd.DataFrame.from_dict` e `pd.read_json`), permitindo a plotagem de gráficos temporais dinâmicos no frontend.
* **Scraping Automatizado e APIs Restritas:** Construção de robôs de coleta de dados sem dependência de drivers pesados (como Selenium), priorizando requisições HTTP leves com a biblioteca `requests`, conforme as boas práticas de ingestão de dados.
* **Engenharia de Prompt e Arquitetura RAG:** Implementação completa de Geração Aumentada de Recuperação usando modelos de embeddings locais (`SentenceTransformers`) e cálculo de similaridade por cosseno para travar o escopo de resposta de uma LLM comercial, mitigando 100% das alucinações.

---

## 👥 Integrantes do Grupo (Turma 2TIAOA - 2026)
* **Davi Santos Ferreira** 
* **Lais Kurahashi** 
* **Lucas Martinelli**

> ⚠️ **Nota de Transparência sobre Versionamento:** Devido a problemas persistentes de autenticação com as credenciais locais do Git e chaves SSH em sua máquina de trabalho, o integrante **Lucas Martinelli** não conseguiu realizar commits diretamente a partir de seu perfil do GitHub neste repositório. Toda a sua contribuição técnica em código (Scraper Web) e documentação foi integrada e buildada no repositório através de pareamento (Pair Programming) com os demais membros da equipe.

---

## 🏗️ Arquitetura do Ecossistema

O projeto divide-se em 4 camadas totalmente integradas:
1.  **Borda Terrestre (IoT):** Microcontrolador ESP32 conectado a sensores DHT22 e MQ-2 para medir temperatura, umidade e fumaça em solo.
2.  **Visão Computacional (Orbital):** Modelo local YOLOv8 que processa imagens de satélite para detecção de focos de fogo/fumaça.
3.  **Automação Web (Ingestão Externa):** Web scraper que consome dados meteorológicos em tempo real (Open-Meteo API) para obter a velocidade do vento regional.
4.  **Camada Generativa (RAG) & Painel:** Motor que cruza os dados obtidos, busca a diretriz correta em um arquivo vetorial local e aciona a LLM do Gemini para gerar o relatório final exposto em um painel Streamlit.

```text
+-----------------------------------------------------------------------+
|                           SatGuard-Edge                               |
+-----------------------------------------------------------------------+
      |                           |                           |
[Visão Orbital]             [Sensor Solo]              [Automação Web]
   YOLOv8                      ESP32                     Scraper API
 (data/raw/)                (DHT22/MQ-2)                (Wind / Humid)
      |                           |                           |
      +---------------------------+---------------------------+
                                  |
                                  v
                     +--------------------------+
                     |  Motor de Fusão de Dados |
                     +--------------------------+
                                  |
                   (Busca por Similaridade de Cosseno)
                                  v
                     +--------------------------+
                     |    Pipeline RAG (Local)  | <--- manual_contingencia.txt
                     +--------------------------+
                                  |
                        (Google Gemini API)
                                  v
                     +--------------------------+
                     |    Dashboard Streamlit   | ---> Relatório Final (.txt)
                     +--------------------------+
