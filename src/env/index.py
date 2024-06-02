import os


def is_prod():
    mode = os.getenv("MODE")
    if mode == 'PROD':
        os.environ['FLASK_ENV'] = 'production'
        return True
    if mode == 'DEV':
        return False
    print("Invalid mode")
    return False


def get_azure_storage_connection_string():
    az = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if az is None:
        raise Exception("Azure Storage Connection String is not set")
    return az


def get_kestra_server():
    kestra_server = os.getenv("KESTRA_SERVER_URL")
    if kestra_server is None:
        raise Exception("Kestra Server is not set")
    return kestra_server
