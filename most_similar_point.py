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

    # Prepare your new data point, used input_params_json
    # new_data = {
    #     'Longitude': 31.896308,
    #     'Latitude': -86.25,
    #     'QSTAR_Mean': np.float32(6.22484e-08),
    #     'QSTAR_Variance': np.float32(5.865151e-13),
    #     'TLML_Mean': np.float32(227.44887),
    #     'TLML_Variance': np.float32(100.015625),
    #     'PRECTOT_Mean': np.float32(2.139298e-06),
    #     'PRECTOT_Variance': np.float32(1.061351e-11),
    #     'QLML_Mean': np.float32(0.000114706956),
    #     'QLML_Variance': np.float32(2.4037654e-08),
    #     'PGENTOT_Mean': np.float32(2.2311021e-06),
    #     'PGENTOT_Variance': np.float32(1.0698551e-11),
    #     'CDQ_Mean': np.float32(0.008105838),
    #     'CDQ_Variance': np.float32(9.229931e-06),
    #     'CDH_Mean': np.float32(0.008105838),
    #     'CDH_Variance': np.float32(9.229931e-06)
    # }

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
        1.0,  # QSTAR_Mean
        1.0,  # QSTAR_Variance
        1.0,  # TLML_Mean
        1.0,  # TLML_Variance
        1.0,  # PRECTOT_Mean
        1.0,  # PRECTOT_Variance
        1.0,  # QLML_Mean
        1.0,  # QLML_Variance
        1.0,  # PGENTOT_Mean
        1.0,  # PGENTOT_Variance
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

    # Optionally, display the location of the most similar data point
    closest_location = closest_data_point[['Longitude', 'Latitude']]
    print(f"Location of the most similar data point: {closest_location.to_dict()}")