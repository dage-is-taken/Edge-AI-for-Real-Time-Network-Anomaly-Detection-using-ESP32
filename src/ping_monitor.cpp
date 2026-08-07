#include "ping_monitor.h"

#include <ESP32Ping.h>

constexpr int PING_COUNT = 10;

PingStats measurePing(IPAddress gateway)
{
    float rtts[PING_COUNT];

    int ok = 0;
    int fail = 0;

    for (int i = 0; i < PING_COUNT; i++)
    {
        if (Ping.ping(gateway, 1))
        {
            rtts[ok++] = Ping.averageTime();
        }
        else
        {
            fail++;
        }

        delay(50);
    }

    PingStats s;

    s.lossPercent = fail * 100.0f / PING_COUNT;

    if (ok == 0)
    {
        s.avgLatency = 999;
        s.jitter = 999;
        return s;
    }

    float sum = 0;

    for (int i = 0; i < ok; i++)
        sum += rtts[i];

    s.avgLatency = sum / ok;

    float jitter = 0;

    for (int i = 1; i < ok; i++)
        jitter += abs(rtts[i] - rtts[i - 1]);

    s.jitter = ok > 1 ? jitter / (ok - 1) : 0;

    return s;
}   