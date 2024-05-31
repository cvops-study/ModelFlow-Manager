import os
import sys
import numpy as np
from azure.index import list_containers, download_blob, download_blobs, extract_metrics
from flask import Flask, render_template, request, redirect, url_for, jsonify
from model.preprocess_image import preprocess_image
from kestra.trigger import trigger_workflow
from model.predict import predict_image

STATIC_PATH = os.path.join(sys.path[1], 'static')

if not os.path.exists(os.path.join(STATIC_PATH, "tmp")):
    os.makedirs(os.path.join(STATIC_PATH, "tmp"))

app = Flask(__name__, template_folder='templates', static_folder=STATIC_PATH)


@app.route('/')
def home():
    return redirect(url_for('models'))


@app.route('/model')
def models():
    containers = list_containers()
    available_models = [container['name'][6:] for container in containers if container['name'].startswith('model-')]
    full_models = []
    for model_name in available_models:
        model_path = os.path.join(STATIC_PATH, 'tmp', model_name)
        if not os.path.exists(os.path.join(model_path, 'results.txt')):
            download_blob('model-' + model_name, "results.txt", model_path)
        metrics = extract_metrics(model_path)
        full_models.append({'name': model_name, 'metrics': metrics})

    return render_template('models.html', len=len(available_models), available_models=full_models, title='Models')


@app.route('/model/<model_name>')
def model(model_name):
    model_path = os.path.join(STATIC_PATH, 'tmp', model_name)
    load = request.args.get('load')
    if not os.path.exists(os.path.join(model_path, 'results.txt')):
        download_blob('model-' + model_name, "results.txt", model_path)
    download_blobs('model-' + model_name, model_path, load)
    images = [image for image in os.listdir(model_path) if image.split(".")[-1] in ["jpeg", "jpg", "png"]]
    metrics = extract_metrics(model_path)

    return render_template('model.html', model=model_name, images=images, title='Model', len=len(images),
                           base_url=model_path, metrics=metrics)


@app.route('/model/<model_name>/predict')
def upload_test(model_name):
    return render_template('upload_img.html', model_name=model_name)


@app.route('/model/<model_name>/predict', methods=['POST'])
def predict(model_name):
    if request.method == 'POST':
        image_file = request.files['file']
        image = np.fromfile(image_file, dtype=np.uint8)
        image = preprocess_image(image)
        if image is None:
            return "Erreur: Impossible de décoder l'image.", 400

        model_file = os.path.join(STATIC_PATH, 'tmp', model_name)
        if os.path.exists(os.path.join(STATIC_PATH, 'tmp', 'runs')):
            os.system("rm -rf " + os.path.join(STATIC_PATH, 'tmp', 'runs'))
        if not os.path.exists(os.path.join(model_file, "best.pt")):
            download_blob('model-' + model_name + "/weights", 'best.pt', model_file)
        predict_image(os.path.join(model_file, "best.pt"), image)
        return render_template('results.html')  # Example for results page
    else:
        return redirect(url_for('home'))


@app.route('/flow')
def flows():
    return render_template('running_flows.html')


@app.route('/flow/trigger')
def trigger_flow():
    return render_template('trigger_flows.html')


@app.route('/flow/train', methods=['POST'])
def train():
    try:
        directory = request.form.get('path')
        tag = request.form.get('tag_2')
        if not os.path.exists(directory):
            raise Exception(f"Directory {directory} does not exist")
        print("bash train_model.sh " + tag + " " + directory)
        status = os.system("bash train_model.sh " + tag + " " + directory)
        if status != 0:
            raise Exception("Failed to start training")
        return redirect(url_for('flows'))
    except Exception as e:
        raise Exception(str(e))


@app.route('/flow/trigger/download', methods=['POST'])
def trigger_download():
    namespace = 'data'
    id = 'load-data'
    try:
        dataset_url = request.form.get('url')
        tag = request.form.get('tag_1')

        res = trigger_workflow(namespace, id, {'dataset_url': dataset_url, 'tag': tag})
        print(res)
        if res['status'] != 'success':
            raise Exception("Failed to trigger download flow", res)
        return redirect(url_for('flows'))

    except Exception as e:
        raise Exception(str(e))

@app.route('/flow/running_flows/test', methods=['GET'])
def running_flows_test():
    try:
        result = get_running_flows(namespace='model', workflow_id='test')
        print(result)
        if result['status'] == 'success':
            return render_template('running_flows.html', flows=result['running_flows'])
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/flow/running_flows/train', methods=['GET'])
def running_flows_train():
    try:
        result = get_running_flows(namespace='model', workflow_id='train')
        print(result)
        if result['status'] == 'success':
            return render_template('running_flows.html', flows=result['running_flows'])
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/flow/running_flows/data', methods=['GET'])
def running_flows_load():
    try:
        result = get_running_flows(namespace='data', workflow_id='load-data')
        print(result)
        if result['status'] == 'success':
            return render_template('running_flows.html', flows=result['running_flows'])
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    
@app.route('/flow/running_flows/all', methods=['GET'])
def running_flows_all():
    try:
        results = []

        # Fetching running flows for each category
        for namespace, workflow_id in [('model', 'test'), ('model', 'train'), ('data', 'load-data')]:
            result = get_running_flows(namespace, workflow_id)
            if result['status'] == 'success':
                results.extend(result['running_flows'])
            else:
                return jsonify({'status': 'error', 'message': result['message']}), 500

        # Sorting by start_time for better readability
        results.sort(key=lambda x: x['start_time'])

        return render_template('running_flows.html', flows=results)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5001)
