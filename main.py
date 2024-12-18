import os
import json
import logging
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict
import ollama

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define paths for logs and uploaded files
FURNITURE_LOG_PATH = 'furniture_state_log.json'
SENSOR_LOG_PATH = 'sensor_log.json'
CAP_IMAGE_PATH = 'cap.jpg'

PROMPT_FILE_PATH = 'Prompt/prompt.txt'        
USER_PROFILE_PATH = 'Prompt/userprofile.txt'
FURNITURE_LIST_PATH = 'Prompt/furniturelist.txt'
CAP_PROMPT_PATH = 'Prompt/CapAnalyzePrompt.txt'

# Initialize conversation history
history = []

def extract_content_inside_braces(text: str) -> str:
    """Extract content inside curly braces."""
    match = re.search(r'\[(.*?)\]', text, re.DOTALL)
    if match:
        return match.group(0)  # Return the entire match, including the braces
    raise ValueError("No content found inside curly braces.")


def load_content_from_file(filepath: str) -> str:
    """Load content from a text file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")
    with open(filepath, 'r') as file:
        return file.read()


def validate_json_format(json_string: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def send_query_to_model(prompt: str, history: List[Dict[str, str]]) -> str:
    """Send a query to the AI model."""
    try:
        history.append({'role': 'user', 'content': prompt})
        response = ollama.chat(model='llama3.1:8b', messages=history)
        return response['message']['content']
    except Exception as e:
        logging.error(f"Error during model interaction: {e}")
        raise


def load_furniture_state_log(log_path: str) -> List[Dict[str, str]]:
    """Load the log file that tracks furniture state changes."""
    if not os.path.exists(log_path):
        # Initialize the log if it doesn't exist
        with open(log_path, 'w') as log_file:
            json.dump([], log_file)
    with open(log_path, 'r') as log_file:
        return json.load(log_file)


def save_furniture_state_log(log_path: str, log_data: List[Dict[str, str]]) -> None:
    """Save the updated furniture state log."""
    with open(log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)


def add_furniture_state_to_log(log_path: str, furniture_state: Dict[str, str]) -> None:
    """Add a new furniture state to the log."""
    log_data = load_furniture_state_log(log_path)
    log_data.append(furniture_state)
    save_furniture_state_log(log_path, log_data)


def get_latest_furniture_state(log_path: str,Reason:bool = False) -> Dict[str, str]:
    """Retrieve the latest furniture state from the log."""
    log_data = load_furniture_state_log(log_path)
    if log_data:
        if Reason:
            return log_data[-1]
        else:
            return log_data[-1][-1]
          # Return the latest state
    return []


def load_sensor_log(sensor_log_path: str) -> List[Dict[str, float]]:
    """Load the sensor log file."""
    if not os.path.exists(sensor_log_path):
        # Initialize the log if it doesn't exist
        with open(sensor_log_path, 'w') as log_file:
            json.dump([], log_file)
    with open(sensor_log_path, 'r') as log_file:
        return json.load(log_file)


def save_sensor_log(sensor_log_path: str, log_data: List[Dict[str, float]]) -> None:
    """Save the updated sensor log file."""
    with open(sensor_log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)


def get_latest_sensor_value(sensor_log_path: str) -> Dict[str, float]:
    """Retrieve the latest sensor value from the log."""
    sensor_data = load_sensor_log(sensor_log_path)
    if sensor_data:
        return sensor_data[-1]  # Return the latest sensor value
    return {}


def validate_sensor_data(sensor_data: Dict[str, float]) -> bool:
    """Validate the structure and content of sensor data."""
    if not isinstance(sensor_data, dict):
        return False
    if 'temperature' not in sensor_data or 'humidity' not in sensor_data:
        return False
    if not isinstance(sensor_data['temperature'], (int, float)):
        return False
    if not isinstance(sensor_data['humidity'], float) or not (0 <= sensor_data['humidity'] <= 1):
        return False
    return True


def cap_analyze(cap_path: str) -> str:
    """Analyze an uploaded photo using the AI model."""
    try:
        content = load_content_from_file(CAP_PROMPT_PATH)
        response = ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': content,
                'images': [cap_path]
            }]
        )
        return response['message']['content']
    except FileNotFoundError:
        logging.error(f"Cap analysis prompt file or image '{cap_path}' not found.")
        return "No image description available."
    except Exception as e:
        logging.error(f"Error during cap analysis: {e}")
        return "Error analyzing image."

def restart_session(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    logging.info("Restarting session due to a critical error.")
    history.clear()
    print("\nSession restarted. Beginning a new session...\n")
    return history

def construct_prompt(user_input: str, furniture_state: Dict, sensor_value: Dict, cap_description: str) -> str:
    """Construct a dynamic prompt for the model."""
    furniture_state_str = f"\n-Current Furniture State: {json.dumps(furniture_state)}" if furniture_state else ""
    sensor_value_str = f"\n-Latest Sensor Value: {json.dumps(sensor_value)}" if sensor_value else ""
    cap_description_str = f"\n-Camera image description: {cap_description}" if cap_description else ""
    return f"-User input: {user_input}{furniture_state_str}{sensor_value_str}{cap_description_str}\nPlease make an appropriate furniture control."

def trim_history(history):
    if len(history) > 5:
        # Keep the first (initial prompt) and the last 5 entries
        return [history[0]] + history[-5:]
    return history

#main user request
@app.route('/send_query', methods=['POST'])
def send_query():
    """Endpoint to send a user query and process it with the AI model."""
    try:
        global history
        data = request.json
        user_input = data.get("user_input", "").strip()
        if not user_input:
            return jsonify({"error": "User input is required."}), 400

        latest_furniture_state = get_latest_furniture_state(FURNITURE_LOG_PATH)
        latest_sensor_value = get_latest_sensor_value(SENSOR_LOG_PATH)
        cap_description = cap_analyze(CAP_IMAGE_PATH)

        prompt = construct_prompt(user_input, latest_furniture_state, latest_sensor_value, cap_description)
        logging.debug(prompt)
        response = send_query_to_model(prompt, history)
        logging.debug(response)

        # Trim history to keep only the initial prompt and the last 5 entries
        history.append({'role': 'user', 'content': user_input})
        history = trim_history(history)

        extracted_result = extract_content_inside_braces(response)
        if validate_json_format(extracted_result):
            furniture_state = json.loads(extracted_result)
            logging.debug(extracted_result)
            add_furniture_state_to_log(FURNITURE_LOG_PATH, furniture_state)
            return jsonify({"message": "New data added to control"}), 200
        else:
            return jsonify({"error": "Model response is not a valid JSON format."}), 500

    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500
    
#fetch furniture state
@app.route('/get_state', methods=['GET'])
def send_furniture_state():
    try:
        data = get_latest_furniture_state(FURNITURE_LOG_PATH,Reason=True)
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Error get furniture state: {e}")
        return jsonify({"error": str(e)}), 500

#upload sensor state   
@app.route('/update_sensor', methods=['POST'])
def update_sensor():
    """Endpoint to update the sensor log."""
    try:
        data = request.json
        sensor_data = data.get("sensor_data", {})
        if not sensor_data:
            return jsonify({"error": "Sensor data is required."}), 400

        if not validate_sensor_data(sensor_data):
            return jsonify({"error": "Invalid sensor data format. Ensure 'temperature' is a number and 'humidity' is a float between 0 and 1."}), 400

        log_data = load_sensor_log(SENSOR_LOG_PATH)
        log_data.append(sensor_data)
        save_sensor_log(SENSOR_LOG_PATH, log_data)

        return jsonify({"message": "Sensor data updated successfully."}), 200

    except Exception as e:
        logging.error(f"Error updating sensor log: {e}")
        return jsonify({"error": str(e)}), 500

#upload photo 
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    """Endpoint to upload a photo to the server."""
    try:
        if 'photo' not in request.files:
            return jsonify({"error": "No photo file provided."}), 400

        file = request.files['photo']
        if file.filename == '':
            return jsonify({"error": "No selected file."}), 400

        file.save(CAP_IMAGE_PATH)
        return jsonify({"message": "Photo uploaded successfully and replaced cap.jpg."}), 200

    except Exception as e:
        logging.error(f"Error uploading photo: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    """Home route to indicate the server is running."""
    return jsonify({"message": "Server is running."}), 200


def setup():
    try:
        initial_prompt = f"{load_content_from_file(PROMPT_FILE_PATH)}{load_content_from_file(USER_PROFILE_PATH)}{load_content_from_file(FURNITURE_LIST_PATH)}\n*Current furniture state:{get_latest_furniture_state(FURNITURE_LOG_PATH)}"
        logging.info("Initial prompt loaded successfully.")
        logging.debug(initial_prompt)
    except FileNotFoundError as e:
        logging.error(e)
        return

    # Add the initial prompt to the conversation history
    global history
    history.append({'role': 'user', 'content': initial_prompt})

    # Send the initial prompt to the model
    try:
        response = send_query_to_model(initial_prompt, history)
        extracted_result = extract_content_inside_braces(response)

        # Validate and log the initial furniture state
        if validate_json_format(extracted_result):
            logging.info("Valid JSON response received from the model.")
            furniture_state = json.loads(extracted_result)
            add_furniture_state_to_log(FURNITURE_LOG_PATH, furniture_state)
            logging.debug(f"Model's Initial Response:{extracted_result}")
        else:
            logging.warning("Model response is not in valid JSON format.")
    except Exception as e:
        logging.error(f"Error during initial interaction: {e}")
        logging.error("system restarting")
        history = restart_session(history)
        setup()
        return  # Restart the session by exiting and allowing the user to re-run


# Run the Flask server
if __name__ == "__main__":    
    setup()
    app.run(host="0.0.0.0", port=5000, debug=True)