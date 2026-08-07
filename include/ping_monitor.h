#pragma once

#include <WiFi.h>

struct PingStats
{
    float avgLatency;
    float jitter;
    float lossPercent;
};

PingStats measurePing(IPAddress gateway);