import mysql.connector
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

MAIL_AUTOR = os.getenv("MAIL_AUTOR")
APP_GMAIL_PASS = os.getenv("APP_GMAIL_PASS")
MAIL_DESTINO = os.getenv("MAIL_DESTINO")

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB")
COLLECTION = os.getenv("COLLECTION")

def connect_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        print("Conexión a la base de datos exitosa.")
        return conn
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        exit(1)

def register_report(cant_registros):
  try:
    client = MongoClient(MONGO_URL)

    db = client[MONGO_DB]
    collection = db[COLLECTION]

    doc = {
      "timestamp": datetime.now() - timedelta(hours=3),
      "area": "Coordinacion",
      "tipo_reporte": "general",
      "cant_enviados": 1,
      "cant_registros": cant_registros
    }

    collection.insert_one(doc)

    print("Registro guardado en MongoDB.")

  except Exception as e:
      print("Error registrando envío en MongoDB:", e)