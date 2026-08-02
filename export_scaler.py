import joblib

scaler = joblib.load("models/scaler.pkl")

print("\nCopy these into your ESP32:\n")

print("MEAN")

for x in scaler.mean_:
    print(f"{x:.6f}f,")

print("\nSTD")

for x in scaler.scale_:
    print(f"{x:.6f}f,")