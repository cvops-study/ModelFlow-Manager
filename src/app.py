import os
import numpy as np
import torch
import cv2
import sys

from flask import Flask, render_template, request, redirect, url_for
from model.preprocess_image import preprocess_image
from azure.index import list_containers, download_blob, download_blobs, extract_metrics

sys.path.append('/src')

STATIC_PATH = os.path.join(sys.path[1], 'static')

app = Flask(__name__, template_folder='templates', static_folder=STATIC_PATH)


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
        device = torch.device('cpu')
        model = torch.load("Model/model.pt", map_location=device)

        # Use your model for prediction
        output_image = model.predict(image)  # Call your model's predict function

        # Save the output image (optional, adjust path)
        cv2.imwrite('output.jpg', output_image)  # Assuming OpenCV for image saving

        # Display the processed image (options: show directly in the browser, redirect to a results page)
        return render_template('results.html', output_image=output_image)  # Example for results page
    else:
        return redirect(url_for('home'))


@app.route('/models')
def models():
    containers = list_containers()
    available_models = [container['name'][6:] for container in containers if container['name'].startswith('model-')]
    for model_name in available_models:
        model_path = STATIC_PATH + '/tmp/' + model_name
        if not os.path.exists(model_path + '/results.txt'):
            download_blob('model-' + model_name, "results.txt", model_path)
    full_models = []
    for model_name in available_models:
        model_path = STATIC_PATH + '/tmp/' + model_name
        metrics = extract_metrics(model_path)
        full_models.append({'name': model_name, 'metrics': metrics})
    return render_template('models.html', len=len(available_models), available_models=full_models, title='Models')


@app.route('/models/<model_name>')
def model(model_name):
    model_path = STATIC_PATH + '/tmp/' + model_name
    load = request.args.get('load')
    if not os.path.exists(model_path) or load == '1':
        download_blobs('model-' + model_name, model_path)
    images = [image for image in os.listdir(model_path) if image.split(".")[-1] in ["jpeg", "jpg", "png"]]
    metrics = extract_metrics(model_path)

    return render_template('model.html', model=model_name, images=images, title='Model', len=len(images),
                           base_url=model_path,metrics=metrics)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
