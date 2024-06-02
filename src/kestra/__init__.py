from src.env.index import get_kestra_server

KESTRA_SERVER = get_kestra_server()
BASE_URL = KESTRA_SERVER + "/api/v1"
