import os
import netCDF4 as nc
import numpy as np
import pandas as pd

# Load the CSV file containing latitude and longitude values
csv_file_path = 'filtered_usa_points.csv'
csv_data = pd.read_csv(csv_file_path)

# Define the folder containing the .nc4 files
data_folder = './MERRA2_Files'

# Define the output folder for the results
output_folder = './data_output_folder'

# Define the variables of interest
variables_of_interest = ['QSTAR', 'TLML', 'PRECTOT', 'QLML', 'PGENTOT', 'CDQ', 'CDH']

# Initialize an empty list to store results for all points
all_results = []

# Adjust this to change the step e.g. step = 2 for every other row
step = 2

# Iterate through every second row in the CSV file (latitude and longitude points)
for index, row in csv_data.iloc[::step].iterrows():
    target_lon = row['Longitude']  # Make sure column names are correct
    target_lat = row['Latitude']    # Make sure column names are correct
    data_point = row['SOYBEAN MATURITY GROUP']  # Extract the data point

    # Initialize dictionaries to store accumulated sums and counts for calculating mean and variance
    accumulated_sum = {var: 0 for var in variables_of_interest}
    accumulated_squared_sum = {var: 0 for var in variables_of_interest}
    count = 0

    # Iterate through each .nc4 file in the folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.nc4'):
            file_path = os.path.join(data_folder, filename)

            # Open the .nc4 file using netCDF4
            with nc.Dataset(file_path, 'r') as dataset:
                # Find the indices of the nearest longitude and latitude to the target
                lons = dataset.variables['lon'][:]
                lats = dataset.variables['lat'][:]
                lon_idx = (np.abs(lons - target_lon)).argmin()
                lat_idx = (np.abs(lats - target_lat)).argmin()

                # Iterate through each variable of interest
                for var in variables_of_interest:
                    if var in dataset.variables:
                        # Read the variable data for the specific lon/lat indices and take the mean over the 'time' dimension
                        data = dataset.variables[var][:, lat_idx, lon_idx]  # 'time' is the first dimension
                        daily_mean = np.mean(data)

                        # Update the accumulated sum and squared sum
                        accumulated_sum[var] += daily_mean
                        accumulated_squared_sum[var] += daily_mean ** 2
                    else:
                        print(f"Missing Variable '{var}' at Lon: {target_lon}, Lat: {target_lat}")

                # Increment the file count
                count += 1

    # Calculate mean and variance for each variable across all days
    mean_values = {var: accumulated_sum[var] / count if count != 0 else np.nan for var in variables_of_interest}
    variance_values = {var: (accumulated_squared_sum[var] / count - (mean_values[var] ** 2)) if count != 0 else np.nan for var in variables_of_interest}

    # Store the results for this specific latitude and longitude
    result_entry = {
        'Longitude': target_lon,
        'Latitude': target_lat,
        'Soybean Maturity Group': data_point  # Include the data point in the result entry
    }

    for var in variables_of_interest:
        result_entry[f'{var}_Mean'] = mean_values[var]
        result_entry[f'{var}_Variance'] = variance_values[var]

    all_results.append(result_entry)

    print(result_entry)  # Check result at every iteration

# Create a DataFrame to store all results
results_df = pd.DataFrame(all_results)

# Save the DataFrame to a JSON file
output_json_path = os.path.join(output_folder, 'reference_data_set.json')  # Specify your desired output file name
results_df.to_json(output_json_path, orient='records', lines=True)
