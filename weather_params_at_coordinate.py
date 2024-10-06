import os
import netCDF4 as nc
import numpy as np
import pandas as pd

def weather_params_at_coordinate(lon_input, lat_input):
    # Define the folder containing the .nc4 files
    data_folder = './MERRA2_Files'

    # Define the variables of interest
    variables_of_interest = ['QSTAR', 'TLML', 'PRECTOT', 'QLML', 'PGENTOT', 'CDQ', 'CDH']

    # Define the target longitude and latitude for which to calculate statistics, this is the info from the function input
    target_lon = lon_input  # Replace with your desired longitude
    target_lat = lat_input   # Replace with your desired latitude

    # Initialize dictionaries to store accumulated sums and counts for calculating mean and variance
    accumulated_sum = {var: 0 for var in variables_of_interest}
    accumulated_squared_sum = {var: 0 for var in variables_of_interest}
    count = 0

    # Iterate through each .nc4 file in the folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.nc4'):
            file_path = os.path.join(data_folder, filename)
            # constructing filepath for the target file

            # Open the .nc4 file using netCDF4
            with nc.Dataset(file_path, 'r') as dataset:
                # Find the indices of the nearest longitude and latitude to the target
                lons = dataset.variables['lon'][:]
                lats = dataset.variables['lat'][:]
                lon_idx = (np.abs(lons - target_lon)).argmin() #argmin() returns the index of the min value in array
                lat_idx = (np.abs(lats - target_lat)).argmin()
                
                # Iterate through each variable of interest
                for var in variables_of_interest:
                    if var in dataset.variables:
                        # Read the variable data for the specific lon/lat indices and take the mean over the 'time' dimension
                        data = dataset.variables[var][:, lat_idx, lon_idx] #time is the first element, Dimensions of variable, eg. 'PRECTOT': ('time', 'lat', 'lon')
                        daily_mean = np.mean(data)
                        
                        # Update the accumulated sum and squared sum
                        accumulated_sum[var] += daily_mean
                        accumulated_squared_sum[var] += daily_mean**2
                    else:
                        print("Missing Variable at" + target_lat + target_lon)

                # Increment the file count
                count += 1

    # Calculate mean and variance for each variable across all days
    mean_values = {var: accumulated_sum[var] / count for var in variables_of_interest}
    variance_values = {var: (accumulated_squared_sum[var] / count) - (mean_values[var]**2) for var in variables_of_interest}

    # Create a DataFrame to store the results
    results_df = pd.DataFrame({
        'Variable': variables_of_interest,
        'Mean': [mean_values[var] for var in variables_of_interest],
        'Variance': [variance_values[var] for var in variables_of_interest]
    })

    # now need to output a JSON from the ds.Dataframe
    json_output = results_df.to_json(orient='records')
    print (json_output) #for testing
    return (json_output, results_df)