import pandas as pd
import numpy as np

num_rows = 300

data = {
    "air_quality_index": np.random.randint(0, 500, num_rows),
    "noise_level": np.random.randint(30, 100, num_rows),
    "green_space_area": np.random.randint(500, 5000, num_rows),
    "land_surface_temp": np.random.uniform(15, 45, num_rows).round(2),
    "mental_health_score": np.random.uniform(1, 10, num_rows).round(2),
    "temperature": np.random.uniform(-10, 50, num_rows).round(2),
    "humidity": np.random.uniform(10, 100, num_rows).round(2),
    "precipitation": np.random.randint(0, 300, num_rows),
    "population_density": np.random.randint(100, 20000, num_rows),
    "crime_rate": np.random.uniform(0, 1, num_rows).round(4),
}

df = pd.DataFrame(data)

file_path = r"C:/Users/GamaZone/Desktop/Coding/urban_mental_health_data.csv"
df.to_csv(file_path, index=False)

print(f"CSV file saved at {file_path}")
