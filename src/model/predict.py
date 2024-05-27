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
        saved_model = torch.hub.load('mkang315/RCS-YOLO', 'custom', path_or_model=model,force_reload=True)
        # Perform inference
        results = saved_model(image)
        # Ensure results are rendered properly
        results.render()
        # Save the output image with bounding boxes
        output_image = results.imgs[0]  # Assuming the first image in the batch
        output_image = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)  # Convert to BGR format for OpenCV
        output_image_path = os.path.join(output_dir, 'output.jpg')
        cv2.imwrite(output_image_path, output_image)

        return output_image_path
    except Exception as e:
        print(f"An error occurred: {e}")
