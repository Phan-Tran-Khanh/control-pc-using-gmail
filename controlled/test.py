from cv2 import VideoCapture, imshow, imwrite

cam_port = 0
camera = VideoCapture(cam_port)

result, image = camera.read()

print(result)
imwrite(filename="img.jpg", img=image)
