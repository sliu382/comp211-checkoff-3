import random
from pathlib import Path

random.seed(42)

SIZES = (10_000, 100_000, 1_000_000, 10_000_000)
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(exist_ok=True)

for size in SIZES:
    output_path = data_dir / f"numbers_{size:_}.txt"
    with output_path.open("w", encoding="utf-8") as file:
        for _ in range(size):
            file.write(f"{random.randint(0, 1000)}\n")
