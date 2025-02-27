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
                                                                                                                                     
lensPosition=8.0                                                                                                                                                                                                                                                                                                                                                                                               def process_image_with_model(image_array):                                                                                    
processed_image = image_array  # This line is just a placeholder                                                                     
return processed_image                                                                                                                                                                                                                                                # Server settings                                                                                                                    
HOST = '192.168.0.55'                                                                                                                
PORT = 1234                                                                                                                                                                                                                                                               # Initialize PiCamera2                                                                                                               
picamera2 = Picamera2()                                                                                                              
modes = picamera2.sensor_modes                                                                                                       
print('This is modes:',modes)
for mode in modes:                                                                                                                       
print("This is mode:",mode)
mode=modes[-1]
preview_config = picamera2.create_still_configuration(buffer_count=1,queue=False,sensor={'output_size':mode['size']},transform=Trans>picamera2.configure(preview_config)

#config = picamera2.create_preview_configuration()
#picamera2.configure(config)
picamera2.start()

#picamera2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": lensPosition})
#picamera2.set_controls({"AfMode": CT.AfModeEnum.Continuous})
with picamera2.controls as controls:
    controls.ExposureTime=100000
exposure_value=100000
# Create and bind the socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
print(f"Server listening on {HOST}:{PORT}")
while True:
    conn, addr = server_socket.accept()
    print(f"Connected by: {addr}")
    #conn.sendall(str('0-200000').encode('utf-8'))
    while True:
        data = conn.recv(1024).decode('utf-8')
        print("this is data:",data)
        print(type(data))
        if not data:
            break
        elif data == "quit":
            print('Quiting')
            conn.close()
            break

        elif data == "shutdown":
            print('shutting down')
            server_socket.close()
            picamera2.stop_preview()
            os.system("shutdown now")

        elif "exposure" in data:
            print("Data:",data)
            exposure_list=data.split('-')
            print("Exposure:",exposure_list)
            exposure_value=int(exposure_list[-1])
            new_controls={"ExposureTime":exposure_value}
            other_config=picamera2.create_still_configuration(controls=new_controls,main={"size":(640,480)})
            picamera2.switch_mode(other_config)
        elif "focusMode" in data:
            pass
        elif "focusValue" in data:
            pass
        elif data=='save':
            pass