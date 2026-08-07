from pathlib import Path

INPUT = "models/model.tflite"
OUTPUT = "../include/model_data.h"

data = Path(INPUT).read_bytes()

with open(OUTPUT, "w") as f:

    f.write("#pragma once\n\n")

    f.write("const unsigned char g_model_data[] = {\n")

    for i, b in enumerate(data):

        if i % 12 == 0:
            f.write("    ")

        f.write(f"0x{b:02x},")

        if i % 12 == 11:
            f.write("\n")
        else:
            f.write(" ")

    f.write("\n};\n\n")

    f.write(f"const unsigned int g_model_data_len = {len(data)};\n")

print("model_data.h generated.")