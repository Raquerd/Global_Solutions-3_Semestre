from ultralytics import YOLO
import os

def iniciar_treinamento():
    print("🔄 Carregando modelo YOLOv8 base...")
    model = YOLO('yolov8n.pt')

    print("🚀 Iniciando o treinamento na GPU...")
    # Executa o treino travando os parâmetros de segurança
    model.train(
        data=r'C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\data\YoLo_Dataset\YOLO_datasets\data.yaml', 
        epochs=50,
        imgsz=640,
        project=r'C:\Users\davih\OneDrive\Documentos\PROJETOS\Fiap\ANO 2\Global Solutions 1\src\YOLO_train\runs\detect\backend_cv',
        name='treinamento_yolo',
        device=0,       # Força o uso da GPU local
        workers=0       # 🔥 CORREÇÃO 2: Evita o estouro de multiprocessing no Windows
    )
