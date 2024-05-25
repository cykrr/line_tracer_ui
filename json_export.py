import json
def create_json_array(data_log):
    arr = []
    for el in data_log:
        timestamp = el[0]
        binary_array = el[1]

        # Create a dictionary with the given data
        data = {
            "timestamp": timestamp,
            "sensor_data": binary_array
        }
        arr.append(data)
    
    # Convert the dictionary to a JSON string
    json_string = json.dumps(arr)
    
    return json_string