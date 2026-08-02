import csv
from pathlib import Path

from training.utils.constants import CSV_HEADER


class DatasetWriter:
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self.file = open(self.output_file, "w", newline="")
        self.writer = csv.DictWriter(self.file, fieldnames=CSV_HEADER)

        self.writer.writeheader()

    def write(self, sample: dict):
        self.writer.writerow(sample)

    def close(self):
        self.file.close()