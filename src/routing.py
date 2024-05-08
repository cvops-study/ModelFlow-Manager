from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/') # ‘https://www.google.com/‘
def home():
	return "Hello world!"

@app.route('/trigger_workflow', methods=['POST'])
def trigger_workflow():
    try:
        # Get the workflow ID from the request
        data = request.get_json(force=True)
        workflow_id = data.get('workflow_id')
        dataset_url = data.get('dataset_url')  # Add this line to get dataset_url from the request

        # Make an API call to trigger the workflow
        response = requests.post(
            f'http://48.216.240.225:8080/api/v1/executions/trigger/{workflow_id}',
            json={'dataset_url': dataset_url}  # Include dataset_url in the JSON payload

        )
        
        if response.status_code == 200:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to trigger workflow'}), response.status_code

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

url = 'http://48.216.240.225:8080/api/v1'

@app.route('/running_flows',methods=['GET'])
def running_flows():
    try:
        # Make a GET request to Kestra API to get the list of running flows
        response = requests.get(f'{url}/execution', params={'namespace': 'flows', 'flowId': 'your_flow_id'})
        if response.status_code == 200:
            running_flows = response.json()
            return jsonify(running_flows)
        else:
            return jsonify({'status': 'error', 'message': 'Failed to fetch running flows'}), response.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
