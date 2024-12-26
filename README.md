# Homie: IoT Furniture Control System  

Homie is an AI-powered system that integrates IoT-enabled furniture, environmental sensors, and image analysis to optimize user comfort, well-being, and energy efficiency. By leveraging advanced prompt engineering techniques and machine learning models, Homie intelligently analyzes user inputs, environmental data, and visual inputs to guide furniture control decisions.  

---

## Features  

- **Dynamic Furniture Control**:  
  Homie processes user input and dynamically adjusts furniture states based on sensor data, image analysis, and user preferences.  

- **Sensor Integration**:  
  Supports temperature and humidity sensors to track environmental conditions and adjust accordingly.  

- **Image Analysis**:  
  Analyzes uploaded images to gain insights into the surrounding environment and assist in decision-making.  

- **AI Interaction**:  
  Uses advanced prompt engineering techniques to interact with AI models for data analysis and decision-making.  

- **JSON Logging**:  
  Logs all furniture state changes and sensor updates in JSON format for transparency and tracking.  

- **RESTful API**:  
  Provides a user-friendly API for querying, updating, and uploading data.  

- **LLM Report**:  
  Use the log to infer user habit and give suggestions

- **Immediate Reminder**:  
  Send an urgent reminder when danger occurs.
  
---

## API Endpoints  

### **1. `/send_query` (POST)**  
**Description:** Processes user input and sends it to the AI model for decision-making.  

- **Request Body:**  
  ```json
  {
      "user_input": "Adjust the furniture for a relaxing evening."
  }
  ```  

- **Response:**  
  - Success:  
    ```json
    {"message": "New data added to control"}
    ```  
  - Error:  
    ```json
    {"error": "Detailed error message"}
    ```  

### **2. `/get_state` (GET)**  
**Description:** Retrieves the latest furniture state.  

- **Response:**  
  ```json
  [
        {
            "Reason": "Your explanation for the decisions, e.g., 'User wants to turn on all the light, and the temperature is too high, so the A/C is set to 24\u7c1eC.'"
        },
        {
            "Smart Adjustable Bed": true,
            "Smart Recliner": false,
            "Smart Lamp": false,
            "Smart Curtains": false,
            "Smart Coffee Table": false,
            "Smart Bookshelf": false,
            "Smart Fan": false,
            "Smart A/C": 24,
            "Smart bathroom Light": true,
            "Smart kitchen Light": true,
            "Smart living room Light": true
        }
    ]
  ```  

### **3. `/update_sensor` (POST)**  
**Description:** Updates the sensor data log.  

- **Request Body:**  
  ```json
  {
    "temperature": 32,
    "humidity": 0.5
  }
  ```  

- **Response:**  
  - Success:  
    ```json
    {"message": "Sensor data updated successfully."}
    ```  
  - Error:  
    ```json
    {"error": "Invalid sensor data format."}
    ```  

### **4. `/upload_photo` (POST)**  
**Description:** Uploads a photo for analysis to assist in decision-making.  

- **Request:**  
  - Form data with the key `photo` for the uploaded image.  

- **Response:**  
  ```json
  {"message": "Photo uploaded successfully and replaced cap.jpg."}
  ```  

### **5. `/` (GET)**  
**Description:** Enter User normal panel.  

- **Response:**  
html webpage
![userpanel](https://github.com/ARRRsunny/Homie/blob/main/assets/userpanel.png)

### **6. `/test_panel` (GET)**  
**Description:** Enter test panel.  

- **Response:**  
html webpage
![testpanel](https://github.com/ARRRsunny/Homie/blob/main/assets/testpanel.png)

### **7. `/send_email_reminder/<id>` (GET)**  
**Description:** send an email reminder to the user.  

- **Response:**
  - Success:  
    ```json
    {'message': 'Email sent successfully'}
    ```  

### **8. `/get_report` (GET)**  
**Description:** send an email about the weekly report of user.  

- **Response:**
  - Success:  
    ```json
    {"message": "Report sent successfully."}
    ```  

---
## Model Used

1. **yolo11m**
2. **llama3.2-vision**
3. **llama3.1:8b**
4. **furniture_llama3.1:latest**
   This model is tuned from llama3.1:8b, specifically tailored for this project. However, its performance is subpar. It's not recommended for use 😭.
   
---

## Prompt Techniques  

The following prompt techniques are used to guide Homie's decision-making:  

1. **Role Specification**:  
   Clearly defines Homie's role as an advanced AI system for analyzing data and controlling IoT-enabled furniture.  

2. **Input Structure and Examples**:  
   Provides detailed categories of input data and examples for better understanding.  

3. **Task Clarification**:  
   Outlines the specific task with clear objectives—maximizing comfort, well-being, and energy efficiency.  

4. **Output Format Specification**:  
   Specifies a JSON-based output format with examples to ensure consistency.  

5. **List and Positioning**:  
   Highlights the importance of the furniture list order, ensuring predictable binary string positioning.  

6. **Constraints and Conditions**:  
   Defines specific control parameters (e.g., ON/OFF states, AC temperature values).  

7. **Example Input and Output**:  
   Demonstrates sample scenarios to improve generalization and accuracy.  

---

## Setup Instructions  

### **1. Requirements**  
- Python 3.10 or higher  
- Flask  
- Flask-CORS  
- ollama Python SDK  
- Dependencies listed in `requirements.txt`  
- ultralytics
  
### **2. Installation**  

1. Clone the repository:  
   ```bash
   git clone https://github.com/your-repo/homie.git
   cd homie
   ```  

2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3. Pull the Model:
   ```bash
   ollama pull llama3.1
   ```
   ```bash
   ollama pull llama3.2-vision
   ```

4. Set up the finetuned model: (Optional,not suggested to use)
   ```bash
   ollama create furniture_llama3.1 -f Main_LLM_model\model\Modelfile
   ```
   modify the main.py
   ```python
   LLM_MODEL = 'furniture_llama3.1:latest'
   ```
5. Modify main.py:
   Adjust the email.
   ```python
    EMAIL_ADDR = 'example@gmail.com'      #the receiver
    EMAIL_AGENT_ADDR = "example@gmail.com"      #agent email, google app passkey
    EMAIL_AGENT_PASS = "password"
   ```
   Adjust the address to your desired setting. If set to 0.0.0.0, your server will be accessible to everyone. You might use [Zerotier](https://www.zerotier.com/) to setup the server
   ```python
     app.run(host="0.0.0.0", port=8080, debug=True)   
   ```
6. Run the server:  
   ```bash
   python main.py
   ```
   
7. Set your browser:  
  Get camera permissions  
  go [chrome://flags/#unsafely-treat-insecure-origin-as-secure](chrome://flags/#unsafely-treat-insecure-origin-as-secure)  
  add the address

6. Access the API at:  
   ```plaintext
   http://localhost:8080
   ```  

---

## File Structure  

```plaintext
homie/
├── cap/
│   ├──cap_processed.jpg
│   ├──cap.jpg
├── app.py
├── requirements.txt
├── userpanel.html
├── webuitester.html
├── yolo11m.pt
├── Prompt/
│   ├── prompt.txt
│   ├── userprofile.txt
│   ├── furniturelist.txt
│   ├── CapAnalyzePrompt.txt
│   ├── preset_reminder.json
│   ├── emailreportprompt.txt
├── logs
│   ├── furniture_state_log.json
│   ├── sensor_log.json
├── iot_control
│   ├── ESP32_receiver.ino
│   ├── PhotoCapture.py
├── Main_LLM_model
│   ├── dataset
│   │   ├── dataset.json
│   ├── model
│   │   ├── Modelfile
│   │   ├── furniture_llama3.1.gguf
│   ├── PhotoCapture.py
└── README.md
```  

---

## Example Usage  

### **Scenario 1: Adjusting for Comfort**  
1. Upload sensor data:  
   ```bash
   curl -X POST http://localhost:5000/update_sensor \
   -H "Content-Type: application/json" \
   -d '{"sensor_data": {"temperature": 22, "humidity": 0.4}}'
   ```  

2. Upload a photo:  
   ```bash
   curl -X POST -F "photo=@path/to/image.jpg" http://localhost:5000/upload_photo
   ```  

3. Send a query:  
   ```bash
   curl -X POST http://localhost:5000/send_query \
   -H "Content-Type: application/json" \
   -d '{"user_input": "Set the room for a cozy movie night."}'
   ```  

4. Retrieve the furniture state:  
   ```bash
   curl http://localhost:5000/get_state
   ```  

---

## Error Handling  

- **Invalid Input:**  
  Returns a detailed error message when user input or sensor data is invalid.  

- **File Not Found:**  
  Logs errors if the required files (prompts, logs) are missing and restarts the session if critical.  

- **AI Model Errors:**  
  Logs any issues during model interaction and provides fallback mechanisms to restart the session.  

---
## Stress Test

- **Direct Input**: "Turn off the light"
  - **Ideal Output**: Light off
- **Complex Input**: "I feel so cool"
  - **Ideal Output**: A/C set to a higher temperature

The test was conducted 50 times for each type of input.

| Direct Input Accuracy | Complex Input Accuracy |
|-----------------------|------------------------|
|          91%          |          76%           |

---
## Future Enhancements 

1. **Authentication and Authorization**:  
   Implement user authentication to secure API endpoints.  

2. **Database Integration**:  
   Replace JSON logs with a robust database for efficient data storage and retrieval.  

3. **Real-Time Updates**:  
   Use WebSocket or MQTT for real-time updates to connected devices.  

4. **Enhanced Image Analysis**:  
   Integrate advanced vision models for more detailed image insights.  

5. **Mobile App Integration**:  
   Develop a mobile app for seamless interaction with Homie.

6. **Enrich the dataset**:  
   Fill more data to finetune the model

---

## License  

This project is licensed under the MIT License. See the `LICENSE` file for more details.  

--- 

## Author  

Developed by [ARRRsunny](https://github.com/ARRRsunny) and [EVBAS](https://github.com/EVBAS). Contributions are welcome!
