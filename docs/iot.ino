#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Definição dos pinos utilizados
#define DHTPIN 15          // Pino digital conectado ao DHT22
#define DHTTYPE DHT22      // Definindo o tipo de sensor DHT
#define MQ2PIN 34          // Pino analógico conectado ao MQ-2 (ADC1_CH6)

// Definição de limiares para a Prova de Conceito (POC)
#define LIMIAR_FUMACA 400  // Valor de leitura analógica considerado crítico

// Configurações do Wi-Fi Simulado do Wokwi
const char* ssid = "Wokwi-GUEST";
const char* password = "Wokwi-GUEST";

// URL da API Backend (Substitua pela URL do backend do Davi ou use um servidor de testes público)
// Exemplo usando o webhook.site para testar o envio se necessário
const char* serverUrl = "http://sua-api-satguard.com/api/telemetria"; 

// Inicialização do sensor DHT
DHT dht(DHTPIN, DHTTYPE);

// Função para conectar ao Wi-Fi
void conectaWiFi() {
  Serial.print("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n[Wi-Fi] Conectado com sucesso!");
  Serial.print("[Wi-Fi] Endereco IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  // Inicializa a comunicação serial para monitoramento
  Serial.begin(115200);
  Serial.println("--- SatGuard-Edge: Inicializando Estacao Terrestre ---");

  // Inicializa o sensor DHT22
  dht.begin();

  // Configura o pino do MQ-2 como entrada analógica
  pinMode(MQ2PIN, INPUT);

  // Inicializa a conexão Wi-Fi
  conectaWiFi();

  Serial.println("Sensores e rede prontos e operacionais.");
  Serial.println("------------------------------------------------");
}

void loop() {
  // Aguarda 5 segundos entre as transmissões para não sobrecarregar a rede/API
  delay(5000);

  // Garante que o ESP32 se reconecte se perder o sinal
  if (WiFi.status() != WL_CONNECTED) {
    conectaWiFi();
  }

  // --- Leituras dos Sensores ---
  float humidade = dht.readHumidity();
  float temperatura = dht.readTemperature(); 
  int nivelFumaca = analogRead(MQ2PIN); 

  // Validação de erro na leitura do DHT22
  if (isnan(humidade) || isnan(temperatura)) {
    Serial.println("[ERRO] Falha ao ler o sensor DHT22! Verifique as conexoes.");
    return;
  }

  // --- Processamento Local Básica ---
  bool alertaLocal = (nivelFumaca > LIMIAR_FUMACA);

  // --- Print Serial de Monitoramento ---
  Serial.print("[Sensor] Temp: "); Serial.print(temperatura, 1);
  Serial.print("°C | Hum: "); Serial.print(humidade, 1);
  Serial.print("% | Smoke: "); Serial.println(nivelFumaca);

  // --- Envio dos Dados via HTTP POST ---
  HTTPClient http;

  // Inicializa a requisição na URL de destino
  http.begin(serverUrl);

  // Configura o cabeçalho para indicar envio de conteúdo JSON
  http.addHeader("Content-Type", "application/json");

  // Monta a string JSON estruturada com os dados coletados
  String jsonPayload = "{";
  jsonPayload += "\"temperatura\":" + String(temperatura, 1) + ",";
  jsonPayload += "\"humidade\":" + String(humidade, 1) + ",";
  jsonPayload += "\"nivel_fumaca\":" + String(nivelFumaca) + ",";
  jsonPayload += "\"alerta_local\":" + String(alertaLocal ? "true" : "false");
  jsonPayload += "}";

  Serial.print("[HTTP] Enviando payload: ");
  Serial.println(jsonPayload);

  // Dispara o método POST enviando a string JSON
  int httpResponseCode = http.POST(jsonPayload);

  // Trata a resposta do servidor/API
  if (httpResponseCode > 0) {
    Serial.print("[HTTP] Código de resposta do servidor: ");
    Serial.println(httpResponseCode);
    String response = http.getString();
    Serial.println("[HTTP] Resposta: " + response);
  } else {
    Serial.print("[ERRO HTTP] Falha ao enviar POST. Código: ");
    Serial.println(httpResponseCode);
  }

  // Libera os recursos da conexão
  http.end();
  Serial.println("------------------------------------------------");
}