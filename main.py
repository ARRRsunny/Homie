import ollama
import re
import json
import logging
import os
from typing import List, Dict

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_content_inside_braces(text: str) -> str:
    match = re.search(r'\{(.*?)\}', text, re.DOTALL)
    if match:
        return match.group(0)  # Return the entire match, including the braces
    raise ValueError("No content found inside curly braces.")


def load_content_from_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")
    with open(filepath, 'r') as file:
        return file.read()


def validate_json_format(json_string: str) -> bool:
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def send_query_to_model(prompt: str, history: List[Dict[str, str]]) -> str:
    try:
        history.append({'role': 'user', 'content': prompt})
        response = ollama.chat(model='llama3.1:8b', messages=history)
        return response['message']['content']
    except Exception as e:
        logging.error(f"Error during model interaction: {e}")
        raise


def restart_session(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    logging.info("Restarting session due to a critical error.")
    history.clear()
    print("\nSession restarted. Beginning a new session...\n")
    return history


def load_furniture_state_log(log_path: str) -> List[Dict[str, str]]:
    """Load the log file that tracks furniture state changes."""
    if not os.path.exists(log_path):
        # Initialize the log if it doesn't exist
        with open(log_path, 'w') as log_file:
            json.dump([], log_file)
    with open(log_path, 'r') as log_file:
        return json.load(log_file)


def save_furniture_state_log(log_path: str, log_data: List[Dict[str, str]]) -> None:
    """Save the updated log file."""
    with open(log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)


def add_furniture_state_to_log(log_path: str, furniture_state: Dict[str, str]) -> None:
    """Add a new furniture state to the log."""
    log_data = load_furniture_state_log(log_path)
    log_data.append(furniture_state)
    save_furniture_state_log(log_path, log_data)


def get_latest_furniture_state(log_path: str) -> str:
    """Retrieve the latest furniture state from the log."""
    log_data = load_furniture_state_log(log_path)
    if log_data:
        return log_data[-1]  # Return the latest state
    return {}


def load_sensor_log(sensor_log_path: str) -> List[Dict[str, str]]:
        """Load the log file that tracks sensor values."""
        if not os.path.exists(sensor_log_path):
            # Initialize the log if it doesn't exist
            with open(sensor_log_path, 'w') as log_file:
                json.dump([], log_file)
        with open(sensor_log_path, 'r') as log_file:
            return json.load(log_file)



def get_latest_sensor_value(sensor_log_path: str) -> Dict[str, str]:
        """Retrieve the latest sensor value from the log."""
        sensor_data = load_sensor_log(sensor_log_path)
        if sensor_data:
            return sensor_data[-1]  # Return the latest sensor value
        return {}

def cap_analyze(cap_path:str) -> str:
    content = load_content_from_file("CapAnalyzePrompt.txt")
    response = ollama.chat(
    model='llama3.2-vision',
    messages=[{
        'role': 'user',
        'content': content,
        'images': [cap_path]
    }])
    return response['message']['content']

def main():
    # Initialize conversation history
    history = []

    # Define the log file path for furniture states
    furniture_log_path = 'furniture_state_log.json'
    sensor_log_path = 'sensor_log.json'
    cap_path = 'cap.jpg'
    # Load the initial prompt
    prompt_file_path = 'prompt.txt'        
    user_profile_path = 'userprofile.txt'
    furniture_list_path = 'furniturelist.txt'
    try:
        initial_prompt = f"{load_content_from_file(prompt_file_path)}{load_content_from_file(user_profile_path)}{load_content_from_file(furniture_list_path)}\n*Sensor data:{get_latest_furniture_state(furniture_log_path)}"
        logging.info("Initial prompt loaded successfully.")
        #print(initial_prompt)
    except FileNotFoundError as e:
        logging.error(e)
        return

    # Add the initial prompt to the conversation history
    history.append({'role': 'user', 'content': initial_prompt})

    # Send the initial prompt to the model
    try:
        response = send_query_to_model(initial_prompt, history)
        extracted_result = extract_content_inside_braces(response)

        # Validate and log the initial furniture state
        if validate_json_format(extracted_result):
            logging.info("Valid JSON response received from the model.")
            furniture_state = json.loads(extracted_result)
            add_furniture_state_to_log(furniture_log_path, furniture_state)
            print("Model's Initial Response:", extracted_result)
        else:
            logging.warning("Model response is not in valid JSON format.")
    except Exception as e:
        logging.error(f"Error during initial interaction: {e}")
        history = restart_session(history)
        return  # Restart the session by exiting and allowing the user to re-run


    while True:
        try:
            # Get the latest furniture state and sensor value
            latest_furniture_state = get_latest_furniture_state(furniture_log_path)
            latest_sensor_value = get_latest_sensor_value(sensor_log_path)

            # Add furniture state and sensor value to the prompt
            latest_furniture_state_str = f"\n-Current Furniture State: {json.dumps(latest_furniture_state)}" if latest_furniture_state else ""
            latest_sensor_value_str = f"\n-Latest Sensor Value: {json.dumps(latest_sensor_value)}" if latest_sensor_value else ""

            # Get user input
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting chat. Goodbye!")
                break
            user_input = f"-User input:{user_input}"
            cap_describe = f"\n-Camera image describsion: {cap_analyze(cap_path)}"
            # Combine user input with the latest furniture state and sensor value
            prompt = f"{user_input}{latest_furniture_state_str}{latest_sensor_value_str}{cap_describe}\nplease make a apporiate furniture control."
            print('*************************************************************************\n',prompt)
            # Send the input to the model
            response = send_query_to_model(prompt, history)

            # Extract and validate the response
            extracted_result = extract_content_inside_braces(response)
            if validate_json_format(extracted_result):
                print("*************************************************************************\n","Model:", extracted_result)
                # Log the new furniture state
                furniture_state = json.loads(extracted_result)
                add_furniture_state_to_log(furniture_log_path, furniture_state)
            else:
                print("*************************************************************************\n","Model response is not in valid JSON format:", extracted_result)

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            choice = input("\nThe model encountered an error. Would you like to restart the session? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                history = restart_session(history)
            else:
                print("Exiting session. Goodbye!")
                break


if __name__ == "__main__":
    main()