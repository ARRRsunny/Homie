import json

# Function to read the existing data from the JSON file
def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data

# Function to write data back to the JSON file
def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to append new data
def append_to_json(file_path, new_data):
    data = read_json(file_path)
    data.append(new_data)
    write_json(file_path, data)

# Define the file path and new data
file_path = 'sensor_log.json'
new_data = {"temperature": 25, "humidity": 0.5}

# Append new data to the JSON file
append_to_json(file_path, new_data)
