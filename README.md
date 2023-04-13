# FastAPI HubSpot-ClickUp Integration

Este es un proyecto que utiliza FastAPI para integrar los servicios de HubSpot y ClickUp, permitiendo crear contactos en HubSpot y sincronizarlos en ClickUp.

## Requisitos

- Python 3.7 o superior
- Una cuenta de HubSpot con una API key
- Una cuenta de ClickUp con una API key y un List ID donde crear los contactos
- Una base de datos PostgreSQL para guardar los registros de las llamadas a la API

## Configuración

1. Clona este repositorio
3. Instala las dependencias: pip install -r requirements.txt

4. Crea un archivo `.env` con las variables de entorno requeridas:


```
HUBSPOT_API_KEY=<tu_api_key_de_hubspot>
CLICKUP_API_KEY=<tu_api_key_de_clickup>
CLICKUP_LIST_ID=<el_id_de_la_lista_de_clickup_en_la_que_quieres_sincronizar>
DB_HOST=<el_host_de_tu_bdd>
DB_PORT=<el_puerto_de_tu_bdd>
DB_USER=<tu_usuario_de_bdd>
DB_PASS=<tu_contraseña_de_bdd>
DB_NAME=<el_nombre_de_tu_bdd>
```


5. Inicia la aplicación: uvicorn main:app --reload


## Uso

### Crear un nuevo contacto

Para crear un nuevo contacto en HubSpot y sincronizarlo en ClickUp, haz una petición POST a la siguiente URL: http://localhost:8000/contacts


La petición debe incluir un cuerpo JSON con la información del contacto:

```json
{
  "email": "ejemplo@ejemplo.com",
  "firstname": "Ejemplo",
  "lastname": "Apellido",
  "phone": "+123456789",
  "website": "https://www.ejemplo.com",
  "estado_clickup": false
}
```








