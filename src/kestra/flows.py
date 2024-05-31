from isodate import Duration
import requests
from datetime import datetime, timedelta
from kestra import BASE_URL

def fetch_running_flows(namespace, start_time, end_time,workflow_id,duration,name):
    response = requests.get(
        f'{BASE_URL}/executions',
        params={
            'namespace': namespace,
            'flowId': workflow_id,
            'startAt': start_time.isoformat() + 'Z',
            'endAt': end_time.isoformat() + 'Z',
            'duration':duration,
            'name':name
        }
    )
    if response.status_code == 200:
        data = response.json()
        running_flows = []
        for execution in data['results']:
            flow_id = execution['id']
            namespace=execution['namespace']
            name=execution['flowId']
            start_time = execution['state']['startDate']
            if execution['state']['current']=="FAILED":
                status="FAILED"
                duration = execution['state'].get('duration')
                end_time = execution['state'].get('endDate')

            elif execution['state']['current']=="RUNNING":
                status="RUNNING"
            else: 
                status="SUCCESS"
                duration = execution['state'].get('duration')
                end_time = execution['state'].get('endDate')


            running_flows.append({
                'flow_id': flow_id,
                'start_time': start_time,
                'end_time': end_time,
                'status': status,
                'duration':duration,
                'namespace':namespace,
                'name':name
            })
            
        return running_flows
    else:
        raise Exception("Failed to fetch running flows: {response.text}")

def get_running_flows(namespace,workflow_id):
    current_time = datetime.utcnow()
    future_time = current_time + timedelta(hours=24)

    running_flows = fetch_running_flows(namespace, current_time, future_time,workflow_id,duration="",name="")

    return {'status': 'success', 'running_flows': running_flows}
