
/*
  anomaly_detector.ino
  Edge AI Network Anomaly Detector
  Measures:
    - Ping latency
    - Jitter
    - Packet loss
    - HTTP throughput (local server)

  Throughput test downloads testfile.bin
  from a Python HTTP server running on your PC.
*/
#include <WiFi.h>
#include <ESP32Ping.h>
#include <HTTPClient.h>
#include <ArduTFLite.h>
#include "model_data.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include <PubSubClient.h>



//==============================
// WiFi Configuration
//============================== 
const float ANOMALY_THRESHOLD = 0.6340072f;
const char* WIFI_SSID = "Ooredoo";
const char* WIFI_PASSWORD = "randompassword";
const char* MQTT_BROKER = "***.***.*.***";  
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "anomaly_detector/data";
const char* MQTT_CLIENT_ID = "esp32_anomaly_detector";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

//==============================
// Local HTTP Server
//==============================

// Your PC IP address
IPAddress speedServer(***,***,*,***);
const int SPEEDTEST_PORT = 8000;
const char* SPEEDTEST_PATH = "/testfile.bin";
//==============================
// Measurement Parameters
//==============================

const int PING_COUNT = 10;

//==============================
// Feature Normalization
//==============================


const float FEATURE_MEAN[8] = {
    3.68482725f,
    2.13458045f,
    0.00000000f,
    3.29817374f,
  -39.06021718f,
   60.93978282f,
    0.47526844f,
    3.29817374f
};

const float FEATURE_STD[8] = {
    2.52624235f,
    3.10005323f,
    1.00000000f,
    0.38818804f,
   15.13817004f,
   15.13817004f,
    0.26117170f,
    0.38818804f
};

//==============================
// Tensor Arena
//==============================

constexpr int kTensorArenaSize = 10 * 1024;
alignas(16) byte tensorArena[kTensorArenaSize];

//==============================
// Globals
//==============================

IPAddress gatewayIP;

struct PingStats {
  float avgLatency;
  float jitter;
  float lossPercent;
};
void connectMQTT() {
    if (mqttClient.connected()) return;

    Serial.print("Connecting to MQTT broker...");

    if (mqttClient.connect(MQTT_CLIENT_ID)) {
        Serial.println(" connected!");
    } else {
        Serial.print(" failed, rc=");
        Serial.println(mqttClient.state());
        // Don't block -- just skip publishing this cycle, retry next loop
    }
}


void setup() {

  delay(1000);

  Serial.begin(115200);

  while (!Serial) {
    delay(10);
  }

  Serial.println();
  Serial.println("==========================================");
  Serial.println(" Edge AI Network Anomaly Detector");
  Serial.println("==========================================");

  // WiFi transmit power
WiFi.setTxPower(WIFI_POWER_19_5dBm);
  Serial.print("Connecting to WiFi");
  Serial.print("WiFi Mode: ");
Serial.println(WiFi.getMode());

Serial.print("Channel: ");
Serial.println(WiFi.channel());

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  WiFi.setSleep(false);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("ERROR: WiFi connection failed!");

    while (true) {
      delay(1000);
    }
  }

  Serial.println("WiFi Connected!");
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);


  Serial.print("ESP32 IP Address : ");
  Serial.println(WiFi.localIP());

  gatewayIP = WiFi.gatewayIP();

  Serial.print("Gateway IP       : ");
  Serial.println(gatewayIP);

  Serial.println();

  Serial.println("Initializing TensorFlow Lite model...");

  if (!modelInit(g_model_data, tensorArena, kTensorArenaSize)) {

    Serial.println("ERROR: Failed to initialize model!");

    while (true) {
      delay(1000);
    }
  }

  Serial.println("Model initialized successfully.");

  Serial.println();
  Serial.print("HTTP Speed Test URL: http://");
Serial.print(speedServer);
  Serial.print(":");
  Serial.print(SPEEDTEST_PORT);
  Serial.println(SPEEDTEST_PATH);

  Serial.println();
  Serial.println("Waiting for measurements...");
  Serial.println("==========================================");
}
//==========================================================
// Measure Ping Statistics
//==========================================================

PingStats measureNetworkPing() {

  float rtts[PING_COUNT];

  int successCount = 0;
  int failCount = 0;

  for (int i = 0; i < PING_COUNT; i++) {

    bool success = Ping.ping(gatewayIP, 1);

    if (success) {
      rtts[successCount] = Ping.averageTime();
      successCount++;
    } else {
      failCount++;
    }

    delay(50);
  }

  PingStats stats;

  stats.lossPercent = (float)failCount * 100.0f / PING_COUNT;

  if (successCount == 0) {

    stats.avgLatency = 999.0f;
    stats.jitter = 999.0f;

    return stats;
  }

  float sum = 0.0f;

  for (int i = 0; i < successCount; i++) {
    sum += rtts[i];
  }

  stats.avgLatency = sum / successCount;

  if (successCount > 1) {

    float jitterSum = 0.0f;

    for (int i = 1; i < successCount; i++) {
      jitterSum += fabs(rtts[i] - rtts[i - 1]);
    }

    stats.jitter = jitterSum / (successCount - 1);

  } else {

    stats.jitter = 0.0f;

  }

  return stats;
}


//==========================================================
// Measure Throughput (Local HTTP Server)
//==========================================================
float measureThroughputMbps()
{
    WiFiClient client;

    if (!client.connect(speedServer, SPEEDTEST_PORT)) {
        Serial.println("Connection failed");
        return -1.0f;
    }

    client.print(String("GET ") + SPEEDTEST_PATH + " HTTP/1.1\r\n" +
                 "Host: " + speedServer.toString() + "\r\n" +
                 "Connection: close\r\n\r\n");

    // skip headers
    while (client.connected()) {
        String line = client.readStringUntil('\n');
        if (line == "\r") break;
    }

    uint8_t buff[4096];
    size_t totalBytes = 0;
    unsigned long startTime = millis();

    while (client.connected() || client.available()) {
        size_t availableSize = client.available();
        if (availableSize) {
            int c = client.read(buff, min(availableSize, sizeof(buff)));
            totalBytes += c;
        }
    }

    unsigned long elapsedMs = millis() - startTime;
    client.stop();

    if (totalBytes == 0 || elapsedMs == 0) return -1.0f;

    float seconds = elapsedMs / 1000.0f;
    float megabits = (totalBytes * 8.0f) / 1000000.0f;

    Serial.print("Downloaded ");
    Serial.print(totalBytes);
    Serial.print(" bytes in ");
    Serial.print(elapsedMs);
    Serial.println(" ms");

    return megabits / seconds;
}
//==========================================================
// Run TensorFlow Lite Inference
//==========================================================
float normalize(float rawValue, int featureIndex)
{
    return (rawValue - FEATURE_MEAN[featureIndex]) /
           FEATURE_STD[featureIndex];
}

float featureWindow[10][8];
int windowIndex = 0;
bool windowReady = false;


float runInference()
{
    float normalizedInput[80];

    int inputIndex = 0;

    for (int t = 0; t < 10; t++)
    {
        for (int f = 0; f < 8; f++)
        {
            normalizedInput[inputIndex] =
                normalize(featureWindow[t][f], f);

            modelSetInput(normalizedInput[inputIndex], inputIndex);

            inputIndex++;
        }
    }

    Serial.println("First window:");

    for (int i = 0; i < 8; i++)
    {
        Serial.print(featureWindow[0][i], 6);
        Serial.print(" ");
    }

    Serial.println();

    Serial.println("First normalized:");

    for (int i = 0; i < 8; i++)
    {
        Serial.print(normalizedInput[i], 6);
        Serial.print(" ");
    }

    Serial.println();

    if (!modelRunInference())
    {
        Serial.println("Inference failed.");
        return -1.0f;
    }

    float mse = 0.0f;

    for (int i = 0; i < 80; i++)
    {
        float output = modelGetOutput(i);

        float diff = normalizedInput[i] - output;

        mse += diff * diff;
    }

    mse /= 80.0f;

    return mse;
}
//==========================================================
// Main Loop
//==========================================================

void loop() {

  Serial.println();
  Serial.println("==========================================");
  Serial.println("New Network Measurement");
  Serial.println("==========================================");

  //-------------------------
  // Ping Test
  //-------------------------

  PingStats pingStats = measureNetworkPing();

  Serial.println();
  Serial.println("Ping Results");

  Serial.print("Average Latency : ");
  Serial.print(pingStats.avgLatency, 2);
  Serial.println(" ms");

  Serial.print("Jitter          : ");
  Serial.print(pingStats.jitter, 2);
  Serial.println(" ms");

  Serial.print("Packet Loss     : ");
  Serial.print(pingStats.lossPercent, 2);
  Serial.println(" %");

  //-------------------------
  // Throughput Test
  //-------------------------

  Serial.println();
  Serial.println("Running HTTP throughput test...");

  float throughput = measureThroughputMbps();

  if (throughput < 0.0f) {
    Serial.println("Throughput test FAILED.");
    throughput = 0.0f;
  } else {
    Serial.print("Throughput      : ");
    Serial.print(throughput, 2);
    Serial.println(" Mbps");
  }

  //-------------------------
  // WiFi Signal Strength
  //-------------------------

  int rssi = WiFi.RSSI();
  Serial.print("RSSI            : ");
  Serial.print(rssi);
  Serial.println(" dBm");

  //-------------------------
  // NEW: Validate measurement before it enters the window
  //-------------------------

  bool measurementValid = (throughput > 0.0f) && (pingStats.avgLatency < 999.0f);

  if (!measurementValid) {
      Serial.println("Invalid measurement, resetting window.");
      windowIndex = 0;
      windowReady = false;
      delay(5000);
      return;
  }

  //-------------------------
  // Run AI Model  (this is your existing code below, unchanged)
  //-------------------------

  float signal_quality = rssi + 100.0f;
  float network_stability = pingStats.jitter / (pingStats.avgLatency + 0.000001f);
  float packet_efficiency = throughput * (1.0f - pingStats.lossPercent / 100.0f);

  featureWindow[windowIndex][0] = pingStats.avgLatency;
featureWindow[windowIndex][1] = pingStats.jitter;
featureWindow[windowIndex][2] = pingStats.lossPercent;
featureWindow[windowIndex][3] = throughput;
featureWindow[windowIndex][4] = rssi;
featureWindow[windowIndex][5] = signal_quality;
featureWindow[windowIndex][6] = network_stability;
featureWindow[windowIndex][7] = packet_efficiency;

windowIndex++;

if (windowIndex >= 10)
{
    windowIndex = 0;
    windowReady = true;
}

if (!windowReady)
{
    Serial.print("Collecting window: ");
    Serial.println(windowIndex);

    delay(5000);
    return;
}
float score = runInference();

Serial.println();

Serial.print("Reconstruction Error : ");
Serial.println(score, 6);

if (score > ANOMALY_THRESHOLD)
{
    Serial.println();
    Serial.println("###############################");
    Serial.println("#   ANOMALY DETECTED!         #");
    Serial.println("###############################");
}
else
{
    Serial.println();
    Serial.println("Traffic Status : NORMAL");
}

//----------------------------------------------------
// Machine-readable output for Python collector
//----------------------------------------------------


Serial.print("DATA,");
unsigned long timestamp = millis();
connectMQTT();

if (mqttClient.connected()) {

    char payload[256];

    snprintf(payload, sizeof(payload),
        "{\"timestamp\":%lu,\"latency_ms\":%.2f,\"jitter_ms\":%.2f,"
        "\"loss_percent\":%.2f,\"throughput_mbps\":%.2f,\"rssi_dbm\":%d,"
        "\"reconstruction_error\":%.6f,\"threshold\":%.7f,\"anomaly\":%s}",
        timestamp,
        pingStats.avgLatency,
        pingStats.jitter,
        pingStats.lossPercent,
        throughput,
        rssi,
        score,
        ANOMALY_THRESHOLD,
        (score > ANOMALY_THRESHOLD) ? "true" : "false"
    );

    mqttClient.publish(MQTT_TOPIC, payload);
    mqttClient.loop();  // needed to maintain the MQTT connection

    Serial.print("MQTT published: ");
    Serial.println(payload);
}

Serial.print(timestamp);
Serial.print(",");

Serial.print(pingStats.avgLatency, 2);
Serial.print(",");

Serial.print(pingStats.jitter, 2);
Serial.print(",");

Serial.print(pingStats.lossPercent, 2);
Serial.print(",");

Serial.print(throughput, 2);
Serial.print(",");

Serial.println(rssi);

Serial.println();
Serial.println("Waiting 5 seconds...");
Serial.println("------------------------------------------");

delay(5000);
}
