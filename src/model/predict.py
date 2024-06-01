import os
import sys
import cv2
import torch

def predict_image(model_path, image):
    try:
        output_dir = os.path.join(sys.path[1], 'static', 'tmp', 'runs')
        os.makedirs(output_dir, exist_ok=True)
        input_image_path = os.path.join(output_dir, "before.jpg")
        cv2.imwrite(input_image_path, image)
        model = torch.load(model_path)
        # Load the custom model
        saved_model = torch.hub.load('mkang315/RCS-YOLO', 'custom', path_or_model=model)
        # Perform inference
        results = saved_model(image)
      # Convert to BGR format for OpenCV
        output_image_path = os.path.join(output_dir)
        results.save(output_image_path)

        return output_image_path
    except Exception as e:
        print(f"An error occurred: {e}")
