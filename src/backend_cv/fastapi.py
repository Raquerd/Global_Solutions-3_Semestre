from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime

app = FastAPI(title="SatGuard-Edge API", version="1.0")

# 1. Definição da estrutura de dados que o ESP32 vai enviar (Pydantic Validation)
class TelemetriaSensor(BaseModel):
    temperatura: float
    humidade: float
    nivel_fumaca: int
    alerta_local: bool

# Banco de dados temporário em memória (Dicionário) para guardar o último registro
historico_telemetria = []

@app.get("/")
def home():
    return {"status": "Operacional", "projeto": "SatGuard-Edge"}

# 2. Endpoint HTTP POST que a Lais vai apontar no código do ESP32
@app.post("/api/telemetria")
def receber_telemetria(dados: TelemetriaSensor):
    try:
        # Adiciona carimbo de data e hora no dado recebido
        dado_consolidado = dados.model_dump()
        dado_consolidado["timestamp"] = datetime.now().isoformat()
        
        # Salva no histórico
        historico_telemetria.append(dado_consolidado)
        
        # Log visual no terminal do servidor para o Davi monitorar
        print(f"\n[DADO RECEBIDO] {dado_consolidado['timestamp']}")
        print(f"-> Temp: {dados.temperatura}°C | Hum: {dados.humidade}%")
        print(f"-> Fumaça (ADC): {dados.nivel_fumaca} | Alerta de Borda: {dados.alerta_local}")
        
        # Se houver alerta de fumaça detectado pelo ESP32, o backend pode disparar gatilhos aqui
        if dados.alerta_local:
            print("⚠️ [SISTEMA] Alerta de solo ativado! Solicitando checagem orbital de Visão Computacional...")

        return {"status": "sucesso", "mensagem": "Dados integrados com sucesso"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar dados: {str(e)}")

# 3. Endpoint GET para o Dashboard da Lais consumir os dados históricos
@app.get("/api/dashboard/dados")
def obter_dados_dashboard():
    # Retorna os últimos 50 registros para plotar gráficos no frontend
    return historico_telemetria[-50:]

if __name__ == "__main__":
    # Roda o servidor localmente na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)