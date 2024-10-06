from flask import Flask, request, jsonify
import json
from weather_params_at_coordinate import weather_params_at_coordinate  # Import the function

app = Flask(__name__)

# Replace the JSON loading with the weather function
def compare_with_first(input_data):
    lon_input = input_data.get('longitude')  # Extract longitude from input data
    lat_input = input_data.get('latitude')   # Extract latitude from input data
    
    # Get the weather data for these coordinates
    weather_data = weather_params_at_coordinate(lon_input, lat_input)
    
    # Parse the weather data JSON
    weather_data_dict = json.loads(weather_data)
    
    comparison_result = {}
    
    # Compare the input data with the weather data
    for key, value in input_data.items():
        if key in weather_data_dict and weather_data_dict[key] == value:
            comparison_result[key] = value
    
    # Save the comparison result to a JSON file
    with open('comparison1_result.json', 'w') as outfile:
        json.dump(comparison_result, outfile)
    
    return comparison_result

# Further compare with second JSON file using the result from step 1
def compare_with_second():
    # Load the result of step 1 from the saved file
    comparison_result = load_json('comparison1_result.json')
    data2 = load_json('data2.json')
    final_result = {}
    
    for key, value in comparison_result.items():
        if value in data2:
            final_result[key] = data2[value]
    
    # Save the final comparison result to a JSON file
    with open('final_comparison_result.json', 'w') as outfile:
        json.dump(final_result, outfile)
    
    return final_result

@app.route('/api', methods=['POST'])
def handle_post():
    input_data = request.json
    
    # Step 1: Compare with weather parameters at given coordinates
    comparison_result = compare_with_first(input_data)
    
    # Step 2: Further compare with second JSON file
    final_result = compare_with_second()
    
    # Return the final result as a JSON response
    return jsonify(final_result)

if __name__ == '__main__':
    app.run(port=5000)

