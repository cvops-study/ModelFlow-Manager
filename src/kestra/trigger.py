import requests
from flask import jsonify
from src.kestra import BASE_URL


def trigger_workflow(namespace, workflow_id, params):
    response = requests.post(
        f'{BASE_URL}/executions/{namespace}/{workflow_id}',
        headers={'Content-Type': 'multipart/form-data'},
        data=params
    )

    if response.status_code == 200:
        return {'status': 'success', 'message': 'Workflow triggered'}
    else:
        return {'status': 'error', 'message': 'Failed to trigger workflow','error':response.json()}
