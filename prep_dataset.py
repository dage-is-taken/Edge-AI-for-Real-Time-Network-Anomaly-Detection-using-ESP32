import pandas as pd

df = pd.read_csv("network_dataset.csv")
df = df.rename(columns={"loss_percent": "packet_loss_percent"})
df["label"] = "normal"  # all real logged data is normal operating conditions
df.to_csv("network_dataset_prepped.csv", index=False)
print(f"Saved {len(df)} rows -> network_dataset_prepped.csv")
