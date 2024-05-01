import os
import sys

sys.path.append('./src')

from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import torch
import cv2 

from preprocess_image import preprocess_image

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

        try:
            # Load and preprocess the image (adapt based on your image format and model requirements)
            image = np.fromfile(image_file, dtype=np.uint8)  # Assuming image data format
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)  # Assuming OpenCV for image processing

            # Check if the image is successfully decoded
            if image is None:
                return "Erreur: Impossible de décoder l'image."

            image = preprocess_image(image)  # Implement your image preprocessing logic
        except Exception as e:
            return f"Erreur lors du prétraitement de l'image : {str(e)}"

        try:
            device = torch.device('cpu' )
            # model = torch.load("src/model/model.pt", map_location=device)["model"]
            model = torch.hub.load('mkang315/RCS-YOLO', 'custom', path_or_model='src/model/model.pt', force_reload=True) 
            res = model(["https://i.imgur.com/QsYnXzR.png"])
            res.print()
            # Use your model for prediction
            output_image = model.predict(image)  # Call your model's predict function

            # Save the output image (optional, adjust path)
            cv2.imwrite('output.jpg', output_image)  # Assuming OpenCV for image saving
        
            # Display the processed image (options: show directly in the browser, redirect to a results page)
            return render_template('results.html', output_image=output_image)  # Example for results page
        except Exception as e:
            raise #return f"Erreur lors de la prédiction : {str(e)}"
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
