import cv2

def preprocess_image(image):

    resized_image = cv2.resize(image, (224, 224))
    normalized_image = resized_image / 255.0

    return normalized_image
