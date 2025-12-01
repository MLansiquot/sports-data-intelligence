import cx_Oracle

USERNAME = "ENV_DATABASE_USER"
PASSWORD = "ENV_DATABASE_PASSWORD"
HOST = "192.168.56.101"
PORT = "1521"
SERVICE_NAME = "orcl"

def get_connection():
    dsn = cx_Oracle.makedsn(HOST, PORT, service_name=SERVICE_NAME)
    return cx_Oracle.connect(user=USERNAME, password=PASSWORD, dsn=dsn)
