import cv2


def preprocess_image(image):
    if is_image_empty(image):
        return None
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    if is_image_empty(image):
        return None
    image = cv2.resize(image, (224, 224))  # Resize to your model's expected input size
    if is_image_empty(image):
        return None
    return image


def is_image_empty(image):
    if image is None:
        return True
    if not image.any():
        return True
    return False
