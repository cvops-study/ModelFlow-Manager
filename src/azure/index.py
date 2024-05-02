import os

from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor

AZURE_STORAGE_CONNECTION_STRING = "AZURE_STORAGE_CONNECTION_STRING"

def get_conn():
    try:
        return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    except Exception as e:
        print(e)
        return None


def list_containers():
    try:
        conn = get_conn()
        if conn:
            return conn.list_containers()
        else:
            print("Connection not established")
            return None
    except Exception as e:
        print(e)
        return None


def download_blob(container_name, blob_name, file_path):
    try:
        conn = get_conn()
        if conn:
            container_client = conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            if "/" in blob_name:
                os.makedirs(file_path + "/" + blob_name.rsplit("/", 1)[0], exist_ok=True)
            with open(file_path + "/" + blob_name, "wb") as f:
                data = blob_client.download_blob()
                data.readinto(f)
        else:
            print("Connection not established")
    except Exception as e:
        print(e)


def download_blobs(container_name, file_path):
    try:
        conn = get_conn()
        if conn:
            container_client = conn.get_container_client(container_name)
            blob_list = container_client.list_blobs()

            if os.path.exists(file_path):
                os.system("rm -rf " + file_path)
            os.makedirs(file_path)

            with ThreadPoolExecutor() as executor:
                futures = []
                for blob in blob_list:
                    if blob.name.split(".")[-1] not in ["jpeg", "jpg", "png"]:
                        continue
                    futures.append(executor.submit(download_blob, container_client, blob.name, file_path))

                for future in futures:
                    future.result()
        else:
            print("Connection not established")
    except Exception as e:
        print(e)


def extract_metrics(model_path):
    with open(model_path+'/results.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) == 0:
            return {}
        last_line = lines[-1].strip().split()
        epochs = int(last_line[0].split('/')[0]) + 1
        metrics = {
            'Epochs': epochs,
            'Precision': float(last_line[-7]),
            'Recall': float(last_line[-6]),
            'mAP@0.5': float(last_line[-5]),
            'mAP@0.5:0.95': float(last_line[-4]),
            'Mean Precision': float(last_line[-3]),
            'Mean Recall': float(last_line[-2])
        }
        return metrics
