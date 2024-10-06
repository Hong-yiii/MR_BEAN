import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist

def most_similar_point(input_params_pandas_df):
    # Load the reference dataset
    file_path = './data_output_folder/reference_data_set.json'
    # Read the JSON file into a DataFrame
    df = pd.read_json(file_path, lines=True)
    print(df.head())

    # Prepare your new data point
    new_df = input_params_pandas_df

    # Define meteorological features (excluding location and target variable)
    meteo_features = [
        'QSTAR_Mean', 'QSTAR_Variance',
        'TLML_Mean', 'TLML_Variance',
        'PRECTOT_Mean', 'PRECTOT_Variance',
        'QLML_Mean', 'QLML_Variance',
        'PGENTOT_Mean', 'PGENTOT_Variance',
        'CDQ_Mean', 'CDQ_Variance',
        'CDH_Mean', 'CDH_Variance'
    ]

    # **Transform new_df to match meteo_features**

    # Initialize an empty dictionary
    data = {}

    # Iterate over each row in new_df to populate the dictionary
    for index, row in new_df.iterrows():
        var = row['Variable']
        mean_col = f"{var}_Mean"
        var_col = f"{var}_Variance"
        data[mean_col] = row['Mean']
        data[var_col] = row['Variance']

    # Include Longitude and Latitude if they are in new_df
    if 'Longitude' in new_df.columns and 'Latitude' in new_df.columns:
        data['Longitude'] = new_df['Longitude'].values[0]
        data['Latitude'] = new_df['Latitude'].values[0]
    else:
        # Assign NaN if not available
        data['Longitude'] = np.nan
        data['Latitude'] = np.nan

    # Create a DataFrame from the dictionary
    new_df_processed = pd.DataFrame([data])

    # Now new_df_processed has columns matching meteo_features
    new_df = new_df_processed

    # Ensure there are no missing values in the meteorological features
    df = df.dropna(subset=meteo_features)

    # Combine reference and new data for consistent scaling
    combined_meteo = pd.concat([df[meteo_features], new_df[meteo_features]], ignore_index=True)

    # Standardize the meteorological features
    scaler = StandardScaler()
    combined_meteo_scaled = scaler.fit_transform(combined_meteo)

    # Split back into reference and new data
    df_scaled_features = combined_meteo_scaled[:-1]
    new_scaled_features = combined_meteo_scaled[-1]

    # Define weights for each feature
    weights = np.array([
        10.0,  # QSTAR_Mean
        10.0,  # QSTAR_Variance
        3.0,  # TLML_Mean
        3.0,  # TLML_Variance
        10.0,  # PRECTOT_Mean
        10.0,  # PRECTOT_Variance
        2.0,  # QLML_Mean
        0.5,  # QLML_Variance
        5.0,  # PGENTOT_Mean
        5.0,  # PGENTOT_Variance
        1.0,  # CDQ_Mean
        1.0,  # CDQ_Variance
        1.0,  # CDH_Mean
        1.0   # CDH_Variance
    ])

    # Optionally, normalize the weights
    weights = weights / np.sum(weights)

    # Apply weights to the scaled features
    df_weighted = df_scaled_features * weights
    new_weighted = new_scaled_features * weights

    # Compute weighted Euclidean distances
    meteo_distances = cdist(df_weighted, [new_weighted], metric='euclidean').flatten()
    df['Meteo_Distance'] = meteo_distances

    # Find the most similar data point
    closest_index = df['Meteo_Distance'].idxmin()
    closest_data_point = df.loc[closest_index]

    # Retrieve the 'Soybean Maturity Group'
    soybean_maturity_group = closest_data_point['Soybean Maturity Group']
    print(f"The most similar data point has a Soybean Maturity Group of: {soybean_maturity_group}")

    # Display the location of the most similar data point
    closest_location = closest_data_point[['Longitude', 'Latitude']]
    print(f"Location of the most similar data point: {closest_location.to_dict()}")

    # Return longitude, latitude, and soybean maturity group
    # return closest_data_point['Longitude'], closest_data_point['Latitude'], soybean_maturity_group
    result = {
        'Longitude': round(float(closest_data_point['Longitude']), 4),
        'Latitude': round(float(closest_data_point['Latitude']), 4),
        'Soybean Maturity Group': float(soybean_maturity_group)
    }
    return result