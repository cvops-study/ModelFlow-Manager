import requests
from flask import jsonify
from src.kestra import BASE_URL


def trigger_workflow(namespace, workflow_id, params):
    response = requests.post(
        f'{BASE_URL}/executions/{namespace}/{workflow_id}',
        json=params
    )

    if response.status_code == 200:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to trigger workflow'}), response.status_code
