
from ultralytics import YOLO
import cv2
import os

# 1. Caminhos de configuração - Alinhar com a estrutura da FIAP
CAMINHO_MODELO = r"C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global solutions copia\src\backend_cv\YOLO_train\runs\detect\backend_cv\treinamento_yolo-3\weights\best.pt"  # Cole o arquivo best.pt baixado nesta pasta

def executar_teste_local(IMAGEM_TESTE, PASTA_DESTINO):
    # Validação de segurança: Verifica se o modelo existe
    if not os.path.exists(CAMINHO_MODELO):
        print(f"[ERRO] Arquivo de pesos '{CAMINHO_MODELO}' não foi encontrado!")
        print("-> Certifique-se de baixar o 'best.pt' do Colab e salvá-lo na pasta correta.")
        return

    # Validação de segurança: Verifica se a imagem de teste existe
    if not os.path.exists(IMAGEM_TESTE):
        print(f"[ERRO] Imagem de teste não encontrada em: {IMAGEM_TESTE}")
        print("-> Salve uma imagem de satélite com esse nome na pasta 'data/raw/' para prosseguir.")
        return

    print("🔄 Carregando modelo YOLOv8 local...")
    # 2. Carrega o modelo com os pesos treinados
    model = YOLO(CAMINHO_MODELO)

    print(f"📸 Executando inferência na imagem: {IMAGEM_TESTE}")
    # 3. Executa a predição
    # conf=40 significa 40% de limiar de confiança (idêntico ao que usavam na API)
    results = model.predict(source=IMAGEM_TESTE, conf=0.4, save=False, verbose=True)

    # 4. Processa os resultados visuais
    for r in results:
        # O método r.plot() desenha as Bounding Boxes (caixas) e as Labels (rótulos) na imagem
        imagem_anotada = r.plot()

        # ─── PARTE NOVA: CRIANDO A VARIÁVEL BOOLEANA E CONFIANÇA ───
        # len(r.boxes) > 0 retornará True se houver detecções, e False se não houver
        localizado = len(r.boxes) > 0 
        
        if localizado:
            confiancas = r.boxes.conf.tolist() 
            maior_confianca = max(confiancas) * 100
            print(f"🚨 [ALERTA] Alvo localizado! Confiabilidade: {maior_confianca:.2f}%")
        else:
            maior_confianca = 0.0
            print("🟢 [ESTÁVEL] Nada foi localizado na imagem.")
        # ──────────────────────────────────────────────────────────

        # Garante que a pasta de destino exista
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        
        # Define o nome do arquivo de saída
        nome_saida = os.path.join(PASTA_DESTINO, "resultado_teste_local.jpg")
        
        # 5. Salva a imagem processada no disco
        cv2.imwrite(nome_saida, imagem_anotada)
        print(f"✅ Sucesso! Imagem anotada salva em: {nome_saida}")
        
        # 🔥 RETORNO COMPLETO: Devolve a booleana e a confiança para o resto do sistema
        return localizado, maior_confianca