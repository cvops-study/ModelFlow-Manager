import os
import sys
import numpy as np
from azure.index import list_containers, download_blob, download_blobs, extract_metrics
from flask import Flask, render_template, request, redirect, url_for, jsonify
from model.preprocess_image import preprocess_image
from kestra.flows import get_running_flows
from kestra.trigger import trigger_workflow
from model.predict import predict_image
from env.index import is_prod

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
        if metrics != {}:
            full_models.append({'name': model_name, 'metrics': metrics})

    return render_template('models.html', len=len(full_models), available_models=full_models, title='Models')


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
def running_flows_all():
    try:
        results = []

        for namespace, workflow_id in [('model', 'test'), ('model', 'train'), ('data', 'load-data')]:
            result = get_running_flows(namespace, workflow_id)
            if result['status'] == 'success':
                results.extend(result['running_flows'])
            else:
                return jsonify({'status': 'error', 'message': result['message']}), 500

        results.sort(key=lambda x: x['start_time'], reverse=True)

        return render_template('running_flows.html', flows=results, type='All')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/flow/test')
def running_flows_test():
    try:
        result = get_running_flows(namespace='model', workflow_id='test')
        if result['status'] == 'success':
            return render_template('running_flows.html', flows=result['running_flows'], type='Test Model')
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/flow/train')
def running_flows_train():
    try:
        result = get_running_flows(namespace='model', workflow_id='train')
        if result['status'] == 'success':
            return render_template('running_flows.html', flows=result['running_flows'], type='Train Model')
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/flow/data')
def running_flows_load():
    try:
        status_filter = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        result = get_running_flows(namespace='data', workflow_id='load-data', status=status_filter,
                                   start_date=start_date, end_date=end_date)
        if result['status'] == 'success':
            return render_template('running_flows.html', flows=result['running_flows'], type='Load Data',
                                   status_filter=status_filter, start_date=start_date, end_date=end_date)
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/flow/trigger')
def trigger_flow():
    return render_template('trigger_flows.html')


@app.route('/flow/trigger/train', methods=['POST'])
def train():
    try:
        directory = request.form.get('path')
        tag = request.form.get('tag_2')
        if not os.path.exists(directory):
            raise Exception(f"Directory {directory} does not exist")
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
        if res['status'] != 'success':
            raise Exception("Failed to trigger download flow", res)
        return redirect(url_for('flows'))

    except Exception as e:
        raise Exception(str(e))

if __name__ == '__main__':
    app.run("0.0.0.0", debug=(not is_prod()), port=5001)
