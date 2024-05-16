import cv2


def preprocess_image(image):
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    resized_image = cv2.resize(image, (224, 224))
    normalized_image = resized_image / 255.0
    return normalized_image
