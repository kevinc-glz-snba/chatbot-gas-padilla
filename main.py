import os 
from fastapi import FastAPI,  Form
from dotenv import load_dotenv
from database import inicializar_db, insertar_tanques_iniciales, actualizar_precio
from twilio.rest import Client 
from bot import procesar_mensaje
load_dotenv()
app = FastAPI()

#Inicializamos a twilio
twilio_client = Client (
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

@app.on_event("startup")
async def startup():
    inicializar_db()
    insertar_tanques_iniciales()

@app.post("/webhook")
async def webhook(Body: str = Form(...), From: str = Form(...)):
    #Print de comprobacion
    print(f"Mensaje recibido: '{Body}' de {From}")
    print(f"OWNER: {os.getenv('OWNER_WHATSAPP')}")
    print(f"¿Es comando de precio? {Body.startswith('/precio')}")
    print(f"¿Es el dueño? {From == os.getenv('OWNER_WHATSAPP')}")
    
    #Comando especial del duenio para actualizar precio por litro
    if Body.startswith("/precio") and From == os.getenv("OWNER_WHATSAPP"):
        valores = Body.split()
        try:
            nuevo_precio = float(valores[1])
            actualizar_precio(nuevo_precio)
            try:
                twilio_client.messages.create(
                    from_ = os.getenv("TWILIO_WHATSAPP_NUMBER"),
                    to = os.getenv("OWNER_WHATSAPP"),
                    body = "El precio por litro y por tanque se ha actualizado con exito."
                )
            except Exception as e:
                print(f"El precio fue actualizado pero no se le pudo notificar al dueño: {e}")
        except ValueError as e:
            try:
                twilio_client.messages.create(
                    from_ = os.getenv("TWILIO_WHATSAPP_NUMBER"),
                    to = os.getenv("OWNER_WHATSAPP"),
                    body = "El valor de precio debe ser numerico"
                )
            except Exception as e:
                print(f"El precio no pudo ser actualizado por que el valor no es compatible pero no se le pudo notificar al dueño: {e}")
        return {"status": "ok"}
    try:
        respuesta = procesar_mensaje(From, Body)
    
        twilio_client.messages.create(
            from_ = os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to = From,
            body = respuesta
        )
        return {"status" : "ok"}
    except Exception as e:
        print(f"ERROR COMPLETO: {e}") 
        return {"status" : "bad", "body": f"Error al procesar la respuesta: {e}"}