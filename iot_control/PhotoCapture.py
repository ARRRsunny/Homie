from ultralytics import YOLO
import cv2 as cv
import json
import requests
import os
import time

def predicting(model, frame, processed_frame_file_address, conf = 0.7, marks=[], generate = False, corner = False, classes=[]):  
    results = model.predict(frame, conf=conf,classes=classes)
    if not results:
        return False
    else:

        for result in results:
            for box in result.boxes:
                mark = [int(box.xyxy[0][0]), int(box.xyxy[0][1]),
                            int(box.xyxy[0][2]), int(box.xyxy[0][3]), 
                            result.names[int(box.cls[0])]]
                marks.append(mark)

        if generate:
            generating(frame, marks, processed_frame_file_address,corner)
        return True
def uploading(address, frame_name, processed_frame_file_address, sub_folder):

    try:

        with open(f"{processed_frame_file_address}/{frame_name}", 'rb') as img_file:
            img_response = requests.post(
                f"{address}/{sub_folder}", 
                files={'photo': img_file})      
            
        print(img_response, img_response.text)

    except ValueError:
        print("failed to send the message to the sever, please check your input data.")  
        img_response = None 

def generating(frame, marks, processed_frame_file_address, corner=False):
    i = 0
    for mark in marks:
        if corner:
            cv.rectangle(frame, (mark[0], mark[1]),
                        (mark[2], mark[3]), (255, 0, 0), 2)
            
        cropped_region = frame[mark[1]:mark[3], 
                          mark[0]:mark[2]]
        print("good")
        name = f"cropped_region_no.{int(i)}--{mark[4]}"
        cv.imwrite(f"{processed_frame_file_address}/{name}.jpg", cropped_region)
        i += 1

    if corner:
        cv.imwrite(f"{processed_frame_file_address}/frame.jpg", cropped_region)

###########################################################################################################

### For images ### 

# model = YOLO("yolo11m.pt")
# processed_file_address = "test Images/Processed"
# img = cv.imread("test Images\Test\Images.jpg")
# add = "test Images/Processed"
# classes = [0]
# IP_address = " " # Your IP address + port 
# sub_folder = " " # Subname of your website
# frame_name = "cropped_region_no.0--person.jpg"
# upload = predicting(model, img, add, generate=True,conf=0.4,classes=classes)
# if upload:
#     uploading(IP_address, frame_name, processed_file_address, sub_folder)

##########################################################################################################

### For video ###

# model = YOLO("yolo11m.pt")
# processed_file_address = "test Images/Processed"
# camera = cv.VideoCapture(0) # Your capture device
# classes = [0]
# counting = False
# init_time = time.time()
# IP_address = " " # Your IP address + port 
# sub_folder = " " # Subname of your website
# frame_name = "cropped_region_no.0--person.jpg"
# while True:

#     ret, frame = camera.read()
#     if not ret:
#         break
#     if time.time() - init_time >= 5:  
#         upload = predicting(model, frame, processed_file_address, generate=True, conf=0.4)
#         if upload:
#             uploading(IP_address, frame_name, processed_file_address, sub_folder)
#         init_time = time.time() 
        



    



    
    