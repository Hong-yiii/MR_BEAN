import netCDF4 as nc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Specify your file name (make sure it is the same as the file in your local directory)
file_name = "MERRA2_20240828testcopy.nc4"

# Open the .nc4 file
dataset = nc.Dataset(file_name, 'r')

# Print basic information about the file
print("File information:")
print(dataset)

# List all variables available in the dataset
print("\nVariables available in the dataset:")
print(dataset.variables.keys())

# Select a specific variable to explore (choose an available variable from the list above)
variable_name = 'QSTAR'  # Replace with any variable from your dataset like 'BSTAR', 'PRECTOT', 'SPEED', etc.

# Check if the variable exists in the dataset
if variable_name in dataset.variables:
    variable_data = dataset.variables[variable_name][:]
    print(f"\nData for variable '{variable_name}':")
    print(variable_data)

    # Get dimensions and metadata
    dimensions = dataset.variables[variable_name].dimensions
    print(f"\nDimensions for variable '{variable_name}': {dimensions}")
    
    # Extract latitude, longitude, and time for reference (if applicable)
    lat = dataset.variables['lat'][:]
    lon = dataset.variables['lon'][:]
    time = dataset.variables['time'][:]

    # Select a slice of data to visualize (e.g., the first time step)
    if variable_data.ndim == 3:
        data_slice = variable_data[0, :, :]  # Slice of the data for the first time step

        # Create a DataFrame for visualization (with latitudes and longitudes)
        df = pd.DataFrame(data_slice, index=lat, columns=lon)
        
        # Create a heatmap of the selected data slice
        plt.figure(figsize=(12, 6))
        sns.heatmap(df, cmap="viridis", cbar=True)
        plt.title(f"Heatmap of {variable_name} at Time Step 0")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.show()
    
    # elif variable_data.ndim == 1:
    #     # If the data is 1D, create a line plot
    #     df = pd.DataFrame(variable_data, columns=[variable_name])
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(df[variable_name], label=variable_name)
    #     plt.title(f"Line Plot of {variable_name}")
    #     plt.xlabel("Index")
    #     plt.ylabel(variable_name)
    #     plt.legend()
    #     plt.grid()
    #     plt.show()

    # Save the DataFrame to CSV (optional)
    csv_file_name = f"{variable_name}.csv"
    df.to_csv(csv_file_name, index=False)
    print(f"\nVariable '{variable_name}' has been saved to {csv_file_name}")

else:
    print(f"Variable '{variable_name}' not found in the dataset. Please check the variable name and try again.")

# Close the dataset
dataset.close()

# ur mother