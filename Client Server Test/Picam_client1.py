import cv2 as cv
import numpy as np
import socket
import time

def adjust_white_balance(image):
    result = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * 0.5)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * 0.5)
    return cv.cvtColor(image, cv.COLOR_BGR2RGB)

def capture_image(server_ip, server_port):
    # Create the socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    
    try:
        # Send the capture command
        start_time = time.time()
        client_socket.sendall("capture".encode('utf-8'))

        # Read the size of the image
        size_data = b""
        while b"<<SIZE>>" not in size_data:
            size_data += client_socket.recv(1024)
        image_size = int(size_data.split(b"<<SIZE>>")[0])

        # Now read exactly image_size bytes
        image_data = b""
        while len(image_data) < image_size:
            to_read = image_size - len(image_data)
            image_data += client_socket.recv(to_read if to_read < 1024 else 1024)

        # Expect the <<END>> marker
        end_marker = client_socket.recv(1024)
        assert end_marker == b'<<END>>', "End marker not received correctly."
        end_time = time.time()
        print("Communication time:", end_time - start_time)

        # Convert the byte data to a numpy array
        nparr = np.frombuffer(image_data, np.uint8)

        # Decode the numpy array into an image
        frame = cv.imdecode(nparr, cv.IMREAD_COLOR)

        # Adjust white balance and return the adjusted image
        return adjust_white_balance(frame)  # Adjust to 6500K

    finally:
        client_socket.close()

# Example usage:
server_ip = '192.168.0.8'
server_port = 1234

image = capture_image(server_ip, server_port)
if image is not None:
    cv.imshow('Captured Image', image)
    cv.waitKey(0)  # Press any key to close the window
    cv.destroyAllWindows()
else:
    print("Failed to capture image.")
