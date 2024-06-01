import requests
from datetime import datetime
from kestra import BASE_URL, KESTRA_SERVER


def fetch_running_flows(namespace, workflow_id):
    response = requests.get(
        f'{BASE_URL}/executions/search',
        params={
            'namespace': namespace,
            'flowId': workflow_id,
            'size': '20',
            'sort': 'state.startDate:desc'
        }
    )

    if response.status_code == 200:
        data = response.json()
        running_flows = []
        for execution in data['results']:
            flow_id = execution['id']
            namespace = execution['namespace']
            name = execution['flowId']
            start_time = format_date(execution['state']['startDate'])
            end_time = ""
            duration = ""
            if execution['state']['current'] == "FAILED" or execution['state']['current'] == "KILLED":
                status = execution['state']['current']
                duration = format_duration(execution['state'].get('duration'))
                end_time = format_date(execution['state'].get('endDate'))
            elif execution['state']['current'] == "RUNNING":
                status = "RUNNING"
            else:
                status = "SUCCESS"
                duration = format_duration(execution['state'].get('duration'))
                end_time = format_date(execution['state'].get('endDate'))

            running_flows.append({
                'url': f'{KESTRA_SERVER}/ui/executions/{namespace}/{name}/{flow_id}/logs',
                'flow_id': flow_id,
                'start_time': start_time,
                'end_time': end_time,
                'status': status,
                'duration': duration,
                'namespace': namespace,
                'name': name
            })

        return running_flows
    else:
        raise Exception("Failed to fetch running flows: {response.text}")


def get_running_flows(namespace, workflow_id):

    running_flows = fetch_running_flows(namespace, workflow_id)

    return {'status': 'success', 'running_flows': running_flows}


def format_date(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')


def format_duration(duration):
    components = duration.split('T')[1]
    days, hours, minutes, seconds = 0, 0, 0, 0

    if 'D' in components:
        split = components.split('D')
        days = int(split[0])
        components = split[1]
    if 'H' in components:
        split = components.split('H')
        hours = int(split[0])
        components = split[1]
    if 'M' in components:
        split = components.split('M')
        minutes = int(split[0])
        components = split[1]
    if 'S' in components:
        split = components.split('S')
        seconds = float(split[0])

    formatted_duration = []
    if days != 0:
        formatted_duration.append(f"{days} days")
    if hours != 0:
        formatted_duration.append(f"{hours} hours")
    if minutes != 0:
        formatted_duration.append(f"{minutes} minutes")
    if seconds != 0:
        formatted_duration.append(f"{seconds} seconds")

    return ", ".join(formatted_duration)
