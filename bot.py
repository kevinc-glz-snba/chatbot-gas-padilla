import os
import json
import pytz
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from database import guardar_mensajes, obtener_historial, obtener_precios, registrar_pedido
from twilio.rest import Client
#Se importa load_dotenv en caso de que bot se ejecute solo
load_dotenv()

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

#Dem md a formato de whatsapp
def markdown_a_whatsapp(texto: str) -> str:
    # Negrita: **texto** → *texto*
    import re
    texto = re.sub(r'\*\*(.*?)\*\*', r'*\1*', texto)
    # Cursiva: *texto* → _texto_ (solo si no es negrita)
    texto = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'_\1_', texto)
    # Eliminar líneas horizontales ---
    texto = re.sub(r'\n---\n', '\n\n', texto)
    # Encabezados # Título → *Título*
    texto = re.sub(r'#{1,6}\s(.*)', r'*\1*', texto)
    return texto

#Funcion para limpiar el json que genere claude
def limpiar_json(texto: str) -> str:
    import re
    texto = re.sub(r'```json\s*', '', texto)
    texto = re.sub(r'```\s*', '', texto)
    return texto.strip()

#Funcion para extaer fecha y hora dentro de nuestra zona horaria
def obtener_hora_mexico():
    zona = pytz.timezone("America/Mexico_City")
    ahora = datetime.now(zona) 
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_semana = dias[ahora.weekday()]
    return f"{dia_semana} {ahora.strftime('%d/%m/%Y %H:%M')}"

def procesar_mensaje(telefono:str, mensaje:str) -> str:
    #Usamos la funcion para almacenar el mensaje del usuario dentro de bd
    guardar_mensajes(telefono, "user", mensaje)
    
    #Guardamos el historial en una variable para poder procesarlo
    #y convertir de tuplas a una lista de diccionarios (role, content)
    mensajes = obtener_historial(telefono)
    conversacion = []
    for mensaje in mensajes:
        message = {
            "role": mensaje[2],
            "content": mensaje[3],
        }
        conversacion.append(message)
    
    #Obtenemos los precios para pasar a claude
    precios = obtener_precios()

    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens= 500,
        system=f""" Fecha y hora actual: {obtener_hora_mexico()}
            Actuarás como un asistente profesional para la proporción de información 
            y toma de pedidos para la Pipa Distribuidora de Gas Padilla No.162. 
            Los datos de dicho distribuidor son los siguientes:

            Horario de servicio: Lunes a Sábado de 7:30am a 5:00pm
            Zonas que cubre: Acambay y colonias aledañas, Atlacomulco, Jocotitlán y Aculco Centro.
            Números de contacto: {os.getenv('CONTACT_PHONE_1')}, {os.getenv('CONTACT_PHONE_2')}

            Precios actuales: {precios}

            El tono con el que responderás a los mensajes será formal y a la vez amigable.

            Cuando soliciten un servicio directo debes solicitar los siguientes datos:
            - Nombre
            - Dirección
            - Cantidad (cuántos litros o pesos desea consumir, el mínimo es de $200 MXN)

            Una vez que tengas nombre, dirección y cantidad, confirma el pedido al cliente e indícale que en breve será atendido.

            Solo toma pedidos dentro del horario de servicio (Lunes a Sábado de 7:30am a 5:00pm). Si alguien solicita servicio fuera de ese horario, indícale el horario disponible y que puede escribir nuevamente al día siguiente o bien puede agendar para el dia que desee el servicio respetando nuestros horario de servicio.

            Cuando alguien pregunte precios o alguna información, proporciónala si cuentas con ella. De lo contrario no alucines, sé honesto e indica que no tienes esa información y proporciona los números de teléfono para hablar directamente con el chofer.

            Responde siempre en español.
            IMPORTANTE - Formato de respuesta:
            Responde SIEMPRE en formato JSON con esta estructura exacta:
            {{
                "mensaje": "tu respuesta al cliente aquí",
                "pedido": null
            }}

            Cuando tengas nombre, dirección y cantidad completos, usa:
            {{
                "mensaje": "confirmación al cliente",
                "pedido": {{
                    "nombre": "nombre del cliente",
                    "direccion": "dirección",
                    "cantidad": "cantidad solicitada",
                    "telefono": "número si lo proporcionó, si no: null"
                }}
            }}

            No agregues texto fuera del JSON. Solo el JSON puro.
        """,
        messages= conversacion
    )
    
    respuesta_claude_texto =  respuesta.content[0].text
    respuesta_limpia = limpiar_json(respuesta_claude_texto)
    print(f"RESPUESTA CLAUDE: '{respuesta_limpia}'")
    respuesta_claude = json.loads(respuesta_limpia)
    
    #Registramos unicamente pedidos cuando se hayan obtenido todos los datos necesarios
    #Al mismo tiempo se le notifica al duenio sobre el nuevo pedido
    if respuesta_claude["pedido"] is not None:
        nombre = respuesta_claude["pedido"]["nombre"]
        direccion = respuesta_claude["pedido"]["direccion"]
        cantidad = respuesta_claude["pedido"]["cantidad"]

        registrar_pedido(nombre, direccion, cantidad, telefono)
        
        #Mensaje para duenio
        mensaje_duenio = f"""
            ---🔔 NUEVO PEDIDO 🔔---
            👤 Nombre del Cliente: {nombre}
            🏠 Direccion: {direccion}
            💲 Cantidad: {cantidad}
            📞 Telefono de contacto: {telefono}
        """
        try:
            twilio_client.messages.create(
                from_ = os.getenv("TWILIO_WHATSAPP_NUMBER"),
                to = os.getenv("OWNER_WHATSAPP"),
                body = mensaje_duenio
            )
            print("Se a notificado al dueño")
        except Exception as e:
            print(f"Error al procesar notifcar al dueño: {e}")
        
    respuesta_wpp = markdown_a_whatsapp(respuesta_claude["mensaje"])
    guardar_mensajes(telefono, "assistant", respuesta_wpp)
    return respuesta_wpp