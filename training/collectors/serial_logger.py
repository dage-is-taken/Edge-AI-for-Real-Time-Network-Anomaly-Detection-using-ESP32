import serial


class SerialLogger:
    def __init__(self, port: str, baudrate: int = 115200):
        self.serial = serial.Serial(
            port,
            baudrate=baudrate,
            timeout=1,
        )

    def readline(self):
        return self.serial.readline().decode(
            "utf-8",
            errors="ignore",
        )

    def close(self):
        self.serial.close()