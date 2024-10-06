from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Load JSON from file
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Compare input with first JSON file (hy data)
def compare_with_first(input_data): #comparison is based on hy function 
    data1 = load_json('data1.json')
    comparison_result = {}
    
    for key, value in input_data.items():
        if key in data1 and data1[key] == value:
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
    
    # Step 1: Compare with first JSON file
    comparison_result = compare_with_first(input_data)
    
    # Step 2: Further compare with second JSON file
    final_result = compare_with_second()
    
    # Return the final result as a JSON response
    return jsonify(final_result)

if __name__ == '__main__':
    app.run(port=5000)
