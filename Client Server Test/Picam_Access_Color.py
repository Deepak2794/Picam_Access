from picamera2 import Picamera2
from libcamera import controls as CT
from libcamera import Transform
import io
import socket
import numpy as np
import cv2
import base64
import os
import json

lensPosition = 8.0

# Server settings
HOST = '192.168.0.54'
PORT = 1234

# Initialize PiCamera2
picamera2 = Picamera2()
modes = picamera2.sensor_modes
print('This is modes:', modes)
for mode in modes:
    print("This is mode:", mode)

mode = modes[-1]
preview_config = picamera2.create_still_configuration(buffer_count=1, queue=False, sensor={'output_size': mode['size']}, transform=Transform(hflip=True, vflip=True))
picamera2.configure(preview_config)

# Configuring preview and starting camera
picamera2.start()

with picamera2.controls as controls:
    controls.ExposureTime = 100000
exposure_value = 100000

# Create and bind the socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
print(f"Server listening on {HOST}:{PORT}")

while True:
    conn, addr = server_socket.accept()
    conn.settimeout(10)  # Set a 10-second timeout for socket operations
    print(f"Connected by: {addr}")

    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            print("this is data:", data)
            print(type(data))
            
            if not data:
                break
            elif data == "quit":
                print('Quitting')
                conn.close()
                break
            elif data == "shutdown":
                print('Shutting down')
                server_socket.close()
                picamera2.stop_preview()
                os.system("shutdown now")
            elif "exposure" in data:
                print("Data:", data)
                exposure_list = data.split('-')
                print("Exposure:", exposure_list)
                exposure_value = int(exposure_list[-1])
                new_controls = {"ExposureTime": exposure_value}
                other_config = picamera2.create_still_configuration(controls=new_controls, main={"size": (640, 480)})
                picamera2.switch_mode(other_config)
            elif "focusMode" in data:
                pass
            elif "focusValue" in data:
                pass
            elif data == 'save':
                pass
            elif data:
                print('Sending data')
                try:
                    # Capture the image into a NumPy array
                    image_array = picamera2.capture_array()
                    processed_image = image_array
                    processed_image = cv2.resize(processed_image, (640, 640), interpolation=cv2.INTER_AREA)
                    # Convert the processed image to JPEG
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]  # JPEG quality
                    result, img_encoded = cv2.imencode('.jpg', processed_image, encode_param)
                    
                    if result:
                        image_data_base64 = base64.b64encode(img_encoded).decode('utf-8')
                        # Create the JSON object
                        payload = {'image': image_data_base64, 'number': data}
                        
                        # Convert JSON object to string
                        json_payload = json.dumps(payload)
                        
                        # Send the size of the JSON payload
                        size_str = str(len(json_payload)).encode('utf-8') + b"<<SIZE>>"
                        conn.sendall(size_str)
                        print("Payload size sent")
                        
                        # Send the JSON payload in chunks
                        conn.sendall(json_payload.encode('utf-8'))
                        print("JSON payload sent")
                        
                        print("Processed image sent successfully.")
                
                except socket.timeout as e:
                    print(f"Timeout error: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")
                

        except socket.timeout:
            print("Socket timeout")
        except Exception as e:
            print(f"An error occurred: {e}")

