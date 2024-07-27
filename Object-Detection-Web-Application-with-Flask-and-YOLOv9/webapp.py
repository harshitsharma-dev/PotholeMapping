import argparse
import io
from PIL import Image
import datetime

import torch
import cv2
import numpy as np
import tensorflow as tf
from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for, Response, jsonify
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess
from subprocess import Popen
import re
import requests
import shutil
import time
import glob
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT
from io import BytesIO



from ultralytics import YOLO


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://avnadmin:AVNS_DV3I8j1B-_b68Vb55Db@mysql-d8392a4-harshitsharma182021-0b7c.g.aivencloud.com:10167/defaultdb?charset=utf8mb4'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# import pymysql
# db = SQLAlchemy(app)
# class RoadDetail(db.Model):
#     __tablename__ = 'ROAD_DETAIL'
#     id = db.Column(db.Integer, primary_key=True)
#     INPUTFILE = db.Column(db.LargeBinary, nullable=False)
#     filename = db.Column(db.String(255), nullable=False)
#     MARKERS = db.Column(LONGTEXT, nullable=True)
#     ROUTEDATA = db.Column(LONGTEXT, nullable=True)
#     OUTPUTFILE = db.Column(db.String(300), nullable=True)
#     OUTPUT = db.Column(LONGTEXT, nullable=True)

# timeout = 10
# connection = pymysql.connect(
#   charset="utf8mb4",
#   connect_timeout=timeout,
#   cursorclass=pymysql.cursors.DictCursor,
#   db="defaultdb",
#   host="mysql-d8392a4-harshitsharma182021-0b7c.g.aivencloud.com",
#   password="AVNS_DV3I8j1B-_b68Vb55Db",
#   read_timeout=timeout,
#   port=10167,
#   user="avnadmin",
#   write_timeout=timeout,
# )

# def load_data():
#     try:
#         cursor = connection.cursor()
#         cursor.execute("Select * from ROAD_DETAIL")
#         data = cursor.fetchall()[1]
#         return data
#     finally:
#         connection.close()


def process_detections(results, pothole_list):
    for result in results:
        pothole_frame = []
        for box in result.boxes:  # Iterate through the bounding boxes
            if box.cls == 3:  # Replace 'pothole' with the correct class name/id
                pothole_frame.append(box.xywh)  # Append bounding box coordinates to the list
        pothole_list.append(pothole_frame)
        print(len(pothole_frame))


def classify_road_quality(pothole_list, batch_size):
    batches = []
    i = 0
    total_frames = len(pothole_list)
    
    while i < total_frames:
        quality = []
        batch = pothole_list[i:i+batch_size]
    

        total_potholes_avg = sum(len(frame) for frame in batch) / len(batch)
        total_area_avg = sum(sum(box[2] * box[3] for box in frame if len(box) >= 4) for frame in batch) / len(batch)
        
        if total_potholes_avg <= 3 and total_area_avg < 1000:
            road_quality = 'very good quality'
        elif total_potholes_avg <= 5 and total_area_avg < 2500:
            road_quality = 'good quality'
        elif total_potholes_avg <= 10 and total_area_avg < 5000:
            road_quality = 'bad quality'
        else:
            road_quality = 'worst quality'
        
        quality.append(road_quality)
        quality.append(i + 1)  # Start frame number
        quality.append(min(i + batch_size, total_frames))  # End frame number
        
        batches.append(quality)
        i += batch_size
        
    print(batches, "This is batches .................................................................................................................")
    return batches

@app.route("/")
def hello_world():
    # latest_file = RoadDetail.query.order_by(RoadDetail.id.desc()).first()
    return render_template('index.html',road_quality = [['empty','empty','empty']],_routeData = '')


# @app.route('/send_data', methods=['POST'])
# def send_data():
#     if request.is_json:
#         data = request.get_json()
#         value = data.get('value')
#         print(f'Received value: {value}')
#         return jsonify({'status': 'success', 'received_value': value})
#     else:
#         return jsonify({'status': 'error', 'message': 'Content-Type must be application/json'}), 415



@app.route("/", methods=["GET", "POST"])
def predict_img():
    
    if request.method == "POST":
        if 'file' in request.files:
            f = request.files['file']                                                            #UPLOAD DATA 1 INPUT FILE
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath,'uploads',f.filename)
            print("upload folder is ", filepath)
            f.save(filepath)
            global imgpath
            predict_img.imgpath = f.filename
            print("printing predict_img :::::: ", predict_img)
                                               
            file_extension = f.filename.rsplit('.', 1)[1].lower() 
            
            if file_extension == 'jpg':
                img = cv2.imread(filepath)

                # Perform the detection
                model = YOLO(r'..\best.pt')
                detections =  model(img, save=True)                  
                pothole = []
                process_detections(detections, pothole)
                print(pothole, "this is pothole")
                road_quality = classify_road_quality(pothole,500)
                print(road_quality, "This is the road quality")                                                        #UPLOAD DATA2 OUTPUT
                # latest_file = RoadDetail.query.order_by(RoadDetail.id.desc()).first()
                return render_template("index.html", road_quality = road_quality)
            
            elif file_extension == 'mp4': 
                video_path = filepath  # replace with your video path
                cap = cv2.VideoCapture(video_path)

                # get video dimensions
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            
                # Define the codec and create VideoWriter object
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (frame_width, frame_height))
                
                # initialize the YOLOv8 model here
                model = YOLO(r'..\best.pt')
                big =  []                                                   
                out = None
                # do YOLOv9 detection on the frame here
                #model = YOLO('yolov9c.pt')
                results = model(video_path, save=True)  #working
                print(results[0].save_dir)
                pothole = []
                process_detections(results, pothole)
                TotalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                print(TotalFrames)
                batch_size = TotalFrames/route_data['Data']['routes'][0]['legs'][0]['summary']['lengthInMeters']                       #taken to cover meter per batch or in other words number of frames per meter
                if batch_size < 1:
                    batch_size = 1
                batch_size = int(batch_size)
                print(batch_size, "This is the batch size calculated...........................................................................................")
                batches = classify_road_quality(pothole,batch_size)                                                                           #UPLOAD DATA2 OUTPUT
                frame_idx = 0
                # road_quality = "unknown"
                output_video_path = 'output_video.mp4'
                counting_frame = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    
                    
                    # Annotate the frame
                    if frame_idx < len(results):
                        result = results[frame_idx]
                        areaSum = 0
                        num_of_pothole = 0
                        for box in result.boxes:
                            if box.cls == 3:  # Replace '3' with the correct class ID for potholes
                                print(box.xywh[0][0].item(), box.xywh[0][1].item(),'it is what it is...............................................................................................................')
                                x, y, w, h = [box.xywh[0][0].item(),box.xywh[0][1].item(),box.xywh[0][2].item(),box.xywh[0][3].item()]
                                
                                x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                area = w * h
                                areaSum += area
                                num_of_pothole += 1
                                cv2.putText(frame, f'Area: {area:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            else:
                                print(box.xywh[0][0].item(), box.xywh[0][1].item(),'it is what it is...............................................................................................................')
                                x, y, w, h = [box.xywh[0][0].item(),box.xywh[0][1].item(),box.xywh[0][2].item(),box.xywh[0][3].item()]
                                
                                x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                names = model.names
                                cv2.putText(frame, f'{names[int(box.cls)]}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if num_of_pothole <= 3 and areaSum < 1000:
                        road_quality = 'very good quality'
                    elif num_of_pothole <= 5 and areaSum < 2500:
                        road_quality = 'good quality'
                    elif num_of_pothole <= 10 and areaSum < 5000:
                        road_quality = 'bad quality'
                    else:
                        road_quality = 'worst quality'
                    # Add the road quality text to the frame
                    cv2.putText(frame, f'Road Quality: {road_quality}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if out is None:
                        h, w = frame.shape[:2]
                        out = cv2.VideoWriter(output_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (w, h))
                    
                    out.write(frame)
                    frame_idx += 1

                cap.release()
                out.release()
                # big.append(road_quality)
                # print(big, 'This is big....................------------------------,,,,,,,,,,,,,,,,,,,,,,,')
                # name = send_data()
                # print(name, 'This is name....................------------------------,,,,,,,,,,,,,,,,,,,,,,,')
                # fpm = road_quality[-1][-1] / request.args.get('value', 1)
                # print(request.args.get('value', 1), "This is .........................................................................")
                # latest_file = RoadDetail.query.order_by(RoadDetail.id.desc()).first()
                return render_template("index.html", road_quality=batches, _routeData =  route_data['Data'])
                    # print(results)
                    # print(road_quality)
                    # cv2.waitKey(1)

                    # res_plotted = results[0].plot()
                    # cv2.imshow("result", res_plotted)
                    
                    # # write the frame to the output video

                    # if cv2.waitKey(1) == ord('q'):
                    #     break

                return video_feed()            


            
    folder_path = 'runs/detect'
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]    
    latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))    
    image_path = folder_path+'/'+latest_subfolder+'/'+f.filename 
    return render_template('index.html', image_path=image_path)
    #return "done"



# #The display function is used to serve the image or video from the folder_path directory.
@app.route('/<path:filename>')
def display(filename):
    folder_path = 'runs/detect'
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]    
    latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))    
    directory = folder_path+'/'+latest_subfolder    
    print("printing directory: ",directory) 
    files = os.listdir(directory)
    latest_file = files[0]
    
    print(latest_file)

    filename = os.path.join(folder_path, latest_subfolder, latest_file)

    file_extension = filename.rsplit('.', 1)[1].lower()

    environ = request.environ
    if file_extension == 'jpg':      
        return send_from_directory(directory,latest_file,environ)

    else:
        return "Invalid file format"
        

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_data = file.read()
        filename = file.filename
        new_entry = RoadDetail(MARKERS="ABC", INPUTFILE=file_data, filename=filename, ROUTEDATA="routedatatry", OUTPUTFILE=file_data, OUTPUT="outputtry")
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))
        
route_data = {'Data':'not found'}
@app.route('/api/route', methods=['POST'])
def api_route():
    # Get the JSON data from the request
    data = request.get_json()
    if data:
        # Process the data (for example, print it)
        print(data)
        route_data['Data'] = data
        # Send a JSON response back to the client
        return jsonify({'status': 'success', 'received_data': data})
    else:
        return jsonify({'status': 'fail', 'message': 'No data received'}), 400

@app.route('/image/<int:file_id>')
def serve_image(file_id):
    file_data = RoadDetail.query.get(file_id)
    if file_data and file_data.OUTPUTFILE:
        return send_file(BytesIO(file_data.INPUTFILE), mimetype='image/jpeg')  # Adjust mimetype as needed
    return "Image not found", 404

def get_frame():
    folder_path = os.getcwd()
    mp4_files = 'output.mp4'
    video = cv2.VideoCapture(mp4_files)  # detected video path
    while True:
        success, image = video.read()
        if not success:
            break
        ret, jpeg = cv2.imencode('.jpg', image) 
      
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')   
        time.sleep(0.1)  #control the frame rate to display one frame every 100 milliseconds: 


# function to display the detected objects video on html page
@app.route("/video_feed")
def video_feed():
    print("function called")

    return Response(get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
        
        


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    parser = argparse.ArgumentParser(description="Flask app exposing yolov9 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()
    # model = YOLO('yolov9c.pt')
    app.run(host="0.0.0.0", port=args.port)
