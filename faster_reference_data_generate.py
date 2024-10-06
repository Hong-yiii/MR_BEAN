import os
import netCDF4 as nc
import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count

# Load the CSV file containing latitude and longitude values
csv_file_path = 'filtered_usa_points.csv'
csv_data = pd.read_csv(csv_file_path)

# Define the folder containing the .nc4 files
data_folder = './MERRA2_Files'

# Define the output folder for the results
output_folder = './data_output_folder'
output_json_path = os.path.join(output_folder, 'reference_data_set.json')

# Define the variables of interest
variables_of_interest = ['QSTAR', 'TLML', 'PRECTOT', 'QLML', 'PGENTOT', 'CDQ', 'CDH']

# Function to process a single row of data
def process_row(row):
    target_lon = row['Longitude']
    target_lat = row['Latitude']
    data_point = row['SOYBEAN MATURITY GROUP']

    accumulated_sum = {var: 0 for var in variables_of_interest}
    accumulated_squared_sum = {var: 0 for var in variables_of_interest}
    count = 0

    for filename in os.listdir(data_folder):
        if filename.endswith('.nc4'):
            file_path = os.path.join(data_folder, filename)

            with nc.Dataset(file_path, 'r') as dataset:
                # Load longitude and latitude only once per file
                lons = dataset.variables['lon'][:]
                lats = dataset.variables['lat'][:]
                lon_idx = (np.abs(lons - target_lon)).argmin()
                lat_idx = (np.abs(lats - target_lat)).argmin()

                for var in variables_of_interest:
                    if var in dataset.variables:
                        data = dataset.variables[var][:, lat_idx, lon_idx]
                        daily_mean = np.mean(data)

                        accumulated_sum[var] += daily_mean
                        accumulated_squared_sum[var] += daily_mean ** 2
                    else:
                        print(f"Missing Variable '{var}' at Lon: {target_lon}, Lat: {target_lat}")

                count += 1

    if count == 0:
        return None

    mean_values = {var: accumulated_sum[var] / count for var in variables_of_interest}
    variance_values = {var: (accumulated_squared_sum[var] / count - (mean_values[var] ** 2)) for var in variables_of_interest}

    result_entry = {
        'Longitude': target_lon,
        'Latitude': target_lat,
        'Soybean Maturity Group': data_point
    }

    for var in variables_of_interest:
        result_entry[f'{var}_Mean'] = mean_values[var]
        result_entry[f'{var}_Variance'] = variance_values[var]

    print(result_entry)
    return result_entry

# Function to write results to JSON incrementally
def write_to_json(results, output_path):
    with open(output_path, 'a') as f:
        for result in results:
            if result is not None:
                f.write(f"{pd.Series(result).to_json()}\n")

# Use multiprocessing to process rows in parallel
if __name__ == '__main__':
    with Pool(cpu_count()) as pool:
        step = 2
        results = pool.map(process_row, [row for _, row in csv_data.iloc[::step].iterrows()])
        write_to_json(results, output_json_path)
