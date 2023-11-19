import cv2
import time

# Load the cascade
face_cascade = cv2.CascadeClassifier(r'C:\Users\ryanr\Documents\OTT\haarcascade_frontalface_default.xml')

# Start capturing video
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Set the update frequency
update_freq = 1  # Hz
update_interval = 1.0 / update_freq

# Initialize the last update time
last_update_time = time.time()

while True:
    # Read the video stream
    ret, frame = cap.read()

    # Convert the image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Draw a rectangle around each face and move the servo motor
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Calculate the center of the face
        center_x = x + w / 2
        center_y = y + h / 2

        # Map the center coordinates to servo angles
        angle_x = int(180 * center_x / frame.shape[1])
        angle_y = int(180 * center_y / frame.shape[0])
        print("Angle X:", angle_x)
        print("Angle Y:", angle_y)

        # Update the servo motor if it's time
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            # Simulate sending data to Arduino by printing
            print("Sending angle_x:", angle_x)
            print("Sending angle_y:", angle_y)
            last_update_time = current_time

    # Display the output
    cv2.imshow('frame', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the resources
cap.release()
cv2.destroyAllWindows()
