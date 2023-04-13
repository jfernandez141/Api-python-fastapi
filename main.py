from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from requests.exceptions import HTTPError
import psycopg2
from sqlalchemy import create_engine,Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Accede a las variables de entorno

hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
clickup_api_key = os.getenv("CLICKUP_API_KEY")
clickup_list_id = os.getenv("CLICKUP_LIST_ID")

#Variables de entorno de la Bdd
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Modelos de datos

class Contact(BaseModel):
    email: str
    firstname: str
    lastname: str
    phone: Optional[str] = None
    website: Optional[str] = None
    estado_clickup: Optional[bool] = False

class APICall(BaseModel):
    fecha: str
    endpoint: str
    parametros: Optional[dict] = None
    resultado: Optional[dict] = None

# Configuración de la app

app = FastAPI()

# Configuración de la base de datos

Base = declarative_base()

# Crea la cadena de conexión
db_uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Crea el objeto Engine de SQLAlchemy
engine = create_engine(db_uri, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

#NIY
class APICallDB(Base):
    __tablename__ = "api_calls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String(50), nullable=False)
    endpoint = Column(String(200), nullable=False)
    parametros = Column(JSON)
    resultado = Column(JSON)

Base.metadata.create_all(engine)

#Definiendo rutas
@app.post("/contacts")
async def create_contact(contact: Contact):
    hubspot_vid = create_contact_in_hubspot(contact)
    clickup_id = sync_contact_clickup(contact)
    log_request(request.url, f"HubSpot VID: {hubspot_vid}, ClickUp ID: {clickup_id}")
    return {"HubSpot VID": hubspot_vid}

# Configuración de la API de HubSpot

headers = {
    "Content-Type": "application/json",
    "Authorization": hubspot_api_key}


hubspot_url = "https://api.hubapi.com/crm/v3/objects/contacts"

# Configuración de la API de ClickUp

clickup_headers = {
    "Authorization": clickup_api_key,
    "Content-Type": "application/json"
}

clickup_base_url = "https://api.clickup.com/api/v2/"

# Funciones auxiliares

def create_contact_in_hubspot(contact: Contact) -> dict:
    data = {
        "properties": [
            {"property": "email", "value": contact.email},
            {"property": "firstname", "value": contact.firstname},
            {"property": "lastname", "value": contact.lastname},
            {"property": "phone", "value": contact.phone},
            {"property": "website", "value": contact.website},
            {"property": "estado_clickup", "value": contact.estado_clickup}
        ]
    }
    response = requests.post(hubspot_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def sync_contact_clickup(contact: Contact):
    url = "https://api.clickup.com/api/v2/contact"
    headers = {
        "Content-Type": "application/json",
        "Authorization": clickup_api_key
    }
    data = {
        "properties": [
            {"property": "email", "value": contact.email},
            {"property": "firstname", "value": contact.firstname},
            {"property": "lastname", "value": contact.lastname},
            {"property": "phone", "value": contact.phone},
            {"property": "website", "value": contact.website},
            {"property": "estado_clickup", "value": contact.estado_clickup}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()["id"]

