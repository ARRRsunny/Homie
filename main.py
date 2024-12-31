import os
import json
import logging
import re
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from typing import List, Dict
import ollama
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from ultralytics import YOLO
import cv2 as cv
import urllib.request as ul
from apscheduler.schedulers.background import BackgroundScheduler

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

#model used
model = YOLO("yolo11m.pt")


LLM_MODEL = 'llama3.1:8b'
#LLM_MODEL = 'furniture_llama3.1:latest'    #tuned model
LLM_VISION_MODEL = 'llama3.2-vision'

# Define paths for logs and uploaded files
FURNITURE_LOG_PATH = 'logs/furniture_state_log.json'
SENSOR_LOG_PATH = 'logs/sensor_log.json'


PROMPT_FILE_PATH = 'Prompt/prompt.txt'        
USER_PROFILE_PATH = 'Prompt/userprofile.txt'
FURNITURE_LIST_PATH = 'Prompt/furniturelist.txt'
CAP_PROMPT_PATH = 'Prompt/CapAnalyzePrompt.txt'
REMINDER_CONTENT_PATH = "Prompt/preset_reminder.json"
EMAIL_REPORT_PATH = 'Prompt/emailreportprompt.txt'

CAP_IMAGE_PATH = 'cap/cap.jpg'
PROCESSD_FILE_PATH = "cap/cap_processed.jpg"

EMAIL_ADDR = 'example@gmail.com'
EMAIL_AGENT_ADDR = "example@gmail.com"
EMAIL_AGENT_PASS = "password"

REPORT_LOG_LENGHT = 10

# Initialize conversation history
history = []

# weekly task
scheduler = BackgroundScheduler()

#############################file handling#############################
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

############################Model handling#############################
def send_query_to_model(prompt: str, history: List[Dict[str, str]]) -> str:
    """Send a query to the AI model."""
    try:
        history.append({'role': 'user', 'content': prompt})
        response = ollama.chat(model=LLM_MODEL, messages=history)
        return response['message']['content']
    except Exception as e:
        logging.error(f"Error during model interaction: {e}")
        raise


def cap_analyze(cap_path: str) -> str:
    """Analyze an uploaded photo using the AI model."""
    try:
        content = load_content_from_file(CAP_PROMPT_PATH)
        response = ollama.chat(
            model= LLM_VISION_MODEL,
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


def predicting(img, save_new_img_path, conf = 0.4, marks=[], Save_new_photo = False, corner = False, classes=[]):  
    global model
    results = model.predict(img, conf=conf,classes=classes)
    if not results:
        return False
    else:
        for result in results:
            for box in result.boxes:
                mark = [int(box.xyxy[0][0]), int(box.xyxy[0][1]),
                            int(box.xyxy[0][2]), int(box.xyxy[0][3]), 
                            result.names[int(box.cls[0])]]
                marks.append(mark)
        if Save_new_photo:
            save_new_image(img, marks, save_new_img_path,corner=corner)
        return True
    
def save_new_image(img, marks, save_new_img_path, corner=False):
    for mark in marks:
        if corner:
            cv.rectangle(img, (mark[0], mark[1]),(mark[2], mark[3]), (255, 0, 0), 2)
        cropped_region = img[mark[1]:mark[3],mark[0]:mark[2]]
        logging.info("YOLO cropped new img")
        cv.imwrite(save_new_img_path, cropped_region)
    if corner:
        cv.imwrite(save_new_img_path, cropped_region)

def image_handling(img_path:str,save_new_img_path:str):
    classes = [0] #person
    img = cv.imread(img_path)
    predicting(img, save_new_img_path, Save_new_photo=True,classes=classes)

def load_reminder_content(Reminder_path: str,id:str) -> str:
    try:
        if not os.path.exists(Reminder_path):
            with open(Reminder_path, 'w') as log_file:
                json.dump({}, log_file)
        with open(Reminder_path, 'r') as log_file:
            try:
                data = json.load(log_file)
            except json.JSONDecodeError:
                raise ValueError(f"The file '{Reminder_path}' contains invalid JSON.")
        if id not in data:
            raise KeyError(f"The key '{id}' does not exist in the log file.")
        return data[id]
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}") from e
    
def trim_history(history):
    if len(history) > 5:
        # Keep the first (initial prompt) and the last 5 entries
        return [history[0]] + history[-5:]
    return history

def weekly_task():
    logging.debug("prepare weekly report")
    send_weekly_report(EMAIL_AGENT_ADDR,EMAIL_AGENT_PASS,EMAIL_ADDR)

def send_weekly_report(email_user, email_pass, email_receiver):
    logging.debug(email_receiver)
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_receiver
    msg['Subject'] = 'Weekly Report'

    body = LLM_intergated_Report()
    logging.debug(body)
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
            logging.debug("Report sent")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def LLM_intergated_Report():
    data = load_furniture_state_log(FURNITURE_LOG_PATH)
    data = data[-REPORT_LOG_LENGHT:] if len(data) >= REPORT_LOG_LENGHT else data
    propmt = load_content_from_file(EMAIL_REPORT_PATH)
    combine_prompt = f"{propmt}here are the recent users' action log:{data}"
    logging.debug(combine_prompt)
    response = ollama.chat(model=LLM_MODEL, messages=[{'role': 'user','content': combine_prompt}])
    logging.debug(response)
    generated_report = response['message']['content']
    logging.debug(generated_report)
    return generated_report

############################Flask server#############################
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
        cap_description = cap_analyze(PROCESSD_FILE_PATH)

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
@app.route('/get_report', methods=['GET'])
def send_report():
    try:
        weekly_task()
        return jsonify({"message": "Report sent successfully."}), 200
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return jsonify({"error": str(e)}), 500

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
        try:
            image_handling(CAP_IMAGE_PATH,PROCESSD_FILE_PATH)
        except Exception as e:
            logging.error(f"Error YOLO cropping: {e}")
            
        return jsonify({"message": "Photo uploaded successfully and replaced cap.jpg."}), 200

    except Exception as e:
        logging.error(f"Error uploading photo: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/send_email_reminder/<id>', methods=['GET'])
def send_email(id):
    logging.debug(EMAIL_ADDR)
    msg = MIMEMultipart()
    msg['From'] = EMAIL_AGENT_ADDR
    msg['To'] = EMAIL_ADDR
    msg['Subject'] = 'EMERGENCY'

    body = load_reminder_content(REMINDER_CONTENT_PATH,id)
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_AGENT_ADDR, EMAIL_AGENT_PASS)
            server.send_message(msg)
            logging.debug("Report sent")
            return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return jsonify({'error': f"Failed to send email: {e}"})

@app.route('/', methods=['GET'])
def serve_html():
    try:
        url = "https://raw.githubusercontent.com/ARRRsunny/Homie/refs/heads/main/userpanel.html"
        with ul.urlopen(url) as client:
            htmldata = client.read().decode('utf-8')
        return htmldata
    except Exception as e:
        logging.error("Error serving HTML: %s", e)
        abort(500, "Internal server error")
    
@app.route('/test_panel', methods=['GET'])
def serve_test_panel():
    try:
        url = "https://raw.githubusercontent.com/ARRRsunny/Homie/refs/heads/main/webuitester.html"
        with ul.urlopen(url) as client:
            htmldata = client.read().decode('utf-8')
        return htmldata
    except Exception as e:
        logging.error("Error serving HTML: %s", e)
        abort(500, "Internal server error")

@app.route('/VoiceContorl', methods=['GET'])
def serve_voice_panel():
    try:
        url = "https://raw.githubusercontent.com/ARRRsunny/Homie/refs/heads/main/speech2text.html"
        with ul.urlopen(url) as client:
            htmldata = client.read().decode('utf-8')
        return htmldata
    except Exception as e:
        logging.error("Error serving HTML: %s", e)
        abort(500, "Internal server error")

##########################Set up##############################
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
    scheduler.add_job(weekly_task, 'cron', day_of_week='sun', hour=20, minute=0)    #Sunday 8.00pm sent report
    setup()
    app.run(host="0.0.0.0", port=8080, debug=True)