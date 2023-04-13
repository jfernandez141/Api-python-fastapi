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
    return create_contact_in_hubspot(contact)


@app.post("/clickup")
async def create_clickup_task(name: dict):
    task = get_clickup_task_by_name(name["name"])
    if task:
        return task
    else:
        return create_clickup_task(name["name"])


@app.get("/clickup/{name}")
async def get_clickup_task(name: str):
    task = get_clickup_task_by_name(name)
    if task:
        return task
    else:
        raise HTTPException(status_code=404, detail="Task not found")


# Configuración de la API de HubSpot

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {hubspot_api_key}"
}

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

def get_clickup_task_by_name(name: str) -> Optional[dict]:
    response = requests.get(clickup_base_url + f"list/{clickup_list_id}/tasks", headers=clickup_headers)
    response.raise_for_status()
    tasks = response.json().get("tasks")
    for task in tasks:
        if task["name"] == name:
            return task
    return None

def create_clickup_task(name: str) -> dict:
    data = {
        "name": name,
        "description": "Nueva tarea creada desde la API de Python",
        "status": "Open",
        "priority": 3
    }
    response = requests.post(clickup_base_url + f"list/{clickup_list_id}/task", headers=clickup_headers, json=data)
    response.raise_for_status()
    return response.json()

