import requests
from datetime import datetime, timedelta
from kestra import BASE_URL

def fetch_running_flows(namespace, start_time, end_time):
    response = requests.get(
        f'{BASE_URL}/executions',
        headers={'Content-Type': 'application/json'},
        params={
            'namespace': namespace,
            'startAt': start_time.isoformat() + 'Z',
            'endAt': end_time.isoformat() + 'Z',
            'status': 'RUNNING'
        }
    )

    if response.status_code == 200:
        data = response.json()
        running_flows = []
        for execution in data['results']:
            flow_id = execution['id']
            start_time = execution['startDate']
            end_time = execution.get('endDate', 'Still running')
            status = execution['state']

            running_flows.append({
                'flow_id': flow_id,
                'start_time': start_time,
                'end_time': end_time,
                'status': status
            })
        return running_flows
    else:
        raise Exception(f"Failed to fetch running flows: {response.text}")

def get_running_flows(namespace):
    current_time = datetime.utcnow()
    future_time = current_time + timedelta(hours=24)

    running_flows = fetch_running_flows(namespace, current_time, future_time)

    return {'status': 'success', 'running_flows': running_flows}
