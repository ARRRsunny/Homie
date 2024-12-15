# Homie - Smart AI Home Assistant  

## Overview  

**Homie** is an advanced AI-powered home assistant designed to analyze various data inputs and control IoT-enabled furniture in a smart home. Homie ensures optimal comfort, convenience, and energy efficiency by dynamically adjusting furniture states based on sensor data, camera image descriptions, and user preferences.

---

## Features  

1. **Role-based Functionality**  
   Homie operates as an intelligent system that manages IoT furniture in a home. It evaluates multiple inputs and determines the most appropriate ON/OFF states or specific settings for each piece of furniture.  

2. **Multi-source Input Analysis**  
   - **Sensor Data**: Includes temperature, humidity, motion detection, pressure sensors, light levels, and noise levels.  
   - **Camera Image Description**: Determines user activity and room state based on visual input (e.g., "The user is lying on the bed and reading.").  
   - **User Profile**: Incorporates age, gender, weight, height, and personalized preferences, such as desired temperature or lighting conditions.  
   - **IoT Furniture List**: A predefined list of IoT-enabled furniture that Homie can control.  

3. **Task Automation**  
   Homie analyzes inputs to automatically determine the optimal state for each piece of furniture. The goal is to enhance user comfort and well-being while maintaining energy efficiency.  

4. **Structured Output**  
   Homie generates outputs in a consistent JSON format, making it easy to integrate with other systems or log results.  

---

## Installation  

To run Homie, ensure you have the necessary dependencies installed.  

1. Clone the repository:  
   ```bash
   git clone https://github.com/your-repo/homie-ai.git
   cd homie-ai
   ```  

2. Install required Python dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  

3. Ensure you have the following files in the project directory:  
   - `prompt.txt`: Contains the main prompt for the AI model.  
   - `furniturelist.txt`: Specifies the list of IoT-enabled furniture.  
   - `userprofile.txt`: Stores user profile details.  
   - `CapAnalyzePrompt.txt`: Contains the vision model prompt for image analysis.  

4. Place the camera image (`cap.jpg`) in the directory for analysis.  

---

## How Homie Works  

### Input Data Sources  

- **Sensor Data**: Provides real-time environmental conditions and activity-related values.  
- **Camera Image Description**: Captures the current state of the room and user activity.  
- **User Profile**: Personalizes settings based on user preferences.  
- **Furniture Log**: Tracks the historical state of IoT furniture.  

### Decision-making Process  

1. **Input Analysis**:  
   Homie evaluates sensor data, analyzes the camera image description, and considers user preferences.  

2. **Task Execution**:  
   Based on the analysis, Homie determines the ON/OFF state or specific settings for each IoT-enabled furniture item.  

3. **Output**:  
   Homie generates a JSON response representing the control states for all furniture.  

### Example Input  

- **Sensor Data**: `{"Temperature": "38°C", "Humidity": "55%", "Motion": "Detected near recliner"}`  
- **Camera Image Description**: `"The user is reclining and watching TV."`  
- **User Profile**:  
  ```json
  {
    "Age": 35,
    "Gender": "Male",
    "Weight": 80,
    "Preferences": {
      "Lighting": "Dim",
      "Temperature": "Cool"
    }
  }
  ```  

### Example Output  

```json
{
  "Smart Adjustable Bed": false,
  "Smart Recliner": true,
  "Smart Desk": false,
  "Smart Lamp": true,
  "Smart Curtains": false,
  "Smart Coffee Table": false,
  "Smart Bookshelf": false,
  "Smart Fan": true,
  "Smart A/C": 26
}
```

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

## Python Implementation  

The system is implemented in Python using the `main.py` script. Key components include:  

1. **Logging and Error Handling**  
   - Logs interactions and monitors errors to maintain session stability.  
   - Includes session restart capability for critical errors.  

2. **JSON Validation**  
   - Ensures outputs are in valid JSON format for seamless integration.  

3. **Session Management**  
   - Maintains a conversation history for context-aware responses.  

4. **Furniture and Sensor Logs**  
   - Tracks changes in furniture states and sensor values over time.  

5. **Camera Image Analysis**  
   - Uses a vision model (`llama3.2-vision`) to describe the current room state.  

6. **Integration with AI Models**  
   - Interacts with `ollama` AI models to process prompts and generate responses.  

---

## Usage  

1. **Run the Main Script**:  
   ```bash
   python main.py
   ```  

2. **Interaction**:  
   - Provide user inputs when prompted.  
   - Homie will analyze the latest sensor data, camera image descriptions, and user preferences to determine the optimal furniture state.  

3. **Exit**:  
   - Type `exit` or `quit` to terminate the session.  

---

## Files and Directories  

- **`main.py`**: Core script to run Homie.  
- **`prompt.txt`**: Primary prompt defining Homie's role and task.  
- **`furniturelist.txt`**: List of IoT-enabled furniture.  
- **`userprofile.txt`**: User profile information.  
- **`CapAnalyzePrompt.txt`**: Prompt for analyzing camera images.  
- **`furniture_state_log.json`**: Log file for tracking furniture states.  
- **`sensor_log.json`**: Log file for tracking sensor data.  
- **`cap.jpg`**: Sample camera image for analysis.  

---

## Contributions  

Feel free to fork this repository and submit pull requests for improvements or additional features.  

---

## License  

This project is licensed under the MIT License.  

---

## Contact  

For questions or feedback, please reach out to [your-email@example.com].
