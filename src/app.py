import os
import sys

sys.path.append('./Model')
from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import torch  # Import PyTorch library
# Assuming best.pt is a PyTorch model saved using torch.save
import cv2

from src.preprocess_image import preprocess_image

app = Flask(__name__)

print(os.getcwd())


# Define routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Get user-uploaded image
        image_file = request.files['image']

        # Load and preprocess the image (adapt based on your image format and model requirements)
        image = np.fromfile(image_file, dtype=np.uint8)  # Assuming image data format
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)  # Assuming OpenCV for image processing
        image = preprocess_image(image)  # Implement your image preprocessing logic
        device = torch.device('cpu' )
        model = torch.load("Model/model.pt" , map_location=device)

        # Use your model for prediction
        output_image = model.predict(image)  # Call your model's predict function

        # Save the output image (optional, adjust path)
        cv2.imwrite('output.jpg', output_image)  # Assuming OpenCV for image saving

        # Display the processed image (options: show directly in the browser, redirect to a results page)
        return render_template('results.html', output_image=output_image)  # Example for results page
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
