# 🤖 Chatbot WhatsApp — Gas Padilla

Bot de WhatsApp con inteligencia artificial para automatizar la atención a clientes y toma de pedidos de la Pipa Distribuidora de Gas Padilla No.162. El bot opera de forma autónoma respondiendo preguntas frecuentes, tomando pedidos y notificando al dueño, todo sin intervención humana.

---

## 🎯 Problema que resuelve

El dueño del negocio recibía decenas de mensajes repetitivos por WhatsApp diariamente (precios, horarios, pedidos), lo que le consumía tiempo y lo distraía de su operación. Este bot automatiza completamente esa atención, permitiéndole enfocarse en el negocio mientras los clientes son atendidos de forma inmediata.

---

## ✨ Características

- Responde preguntas frecuentes automáticamente (precios, horarios, zonas de cobertura)
- Toma pedidos recopilando nombre, dirección y cantidad
- Valida horario de servicio en tiempo real (no acepta pedidos fuera de horario)
- Notifica al dueño por WhatsApp cuando llega un nuevo pedido
- Registra todos los pedidos en base de datos
- Comando `/precio` para que el dueño actualice precios semanalmente
- Historial de conversación persistente por cliente
- Formato de texto compatible con WhatsApp

---

## 🛠️ Tecnologías utilizadas

- **Python + FastAPI** — Servidor backend y webhook
- **Twilio API** — Integración con WhatsApp
- **Claude API (Anthropic)** — Motor de inteligencia artificial
- **SQLite** — Base de datos para pedidos e historial
- **ngrok** — Túnel para desarrollo local
- **python-dotenv** — Manejo seguro de credenciales

---

## 📁 Estructura del proyecto

```
chatbot-gas-padilla/
├── main.py         ← Servidor FastAPI y webhook de Twilio
├── bot.py          ← Lógica del bot y conexión con Claude
├── database.py     ← Base de datos SQLite y funciones CRUD
├── requirements.txt
├── Procfile        ← Configuración de despliegue
└── .env            ← Credenciales (no incluido)
```

---

## ⚙️ Cómo correrlo localmente

### Requisitos previos
- Python 3.11+
- Cuenta en [Twilio](https://twilio.com) con Sandbox de WhatsApp activado
- Cuenta en [Anthropic Console](https://console.anthropic.com) con API key
- [ngrok](https://ngrok.com) instalado

### 1. Clona el repositorio

```bash
git clone https://github.com/kevinc-glz-snba/chatbot-gas-padilla.git
cd chatbot-gas-padilla
```

### 2. Crea el entorno virtual e instala dependencias

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configura las variables de entorno

Crea un archivo `.env`:

```
ANTHROPIC_API_KEY=tu_api_key_aqui
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
OWNER_WHATSAPP=whatsapp:+52XXXXXXXXXX
```

### 4. Inicia el servidor

```bash
uvicorn main:app --reload
```

### 5. Expón el servidor con ngrok

```bash
ngrok http 8000
```

Copia la URL de ngrok y configúrala en Twilio como webhook:
```
https://tu-url.ngrok-free.app/webhook
```

---

## 💬 Uso

### Como cliente
Manda cualquier mensaje al número de WhatsApp del negocio. El bot responderá automáticamente con información o iniciará el proceso de toma de pedido.

### Como dueño
Actualiza el precio por litro mandando:
```
/precio 13.50
```
El bot actualizará automáticamente los precios de todos los tanques y confirmará el cambio.

---

## 📚 Lo que aprendí construyendo este proyecto

- **Webhooks:** Cómo recibir eventos externos en tiempo real desde servicios como Twilio, invirtiendo el flujo tradicional de peticiones
- **Form Data vs JSON:** Por qué servicios como Twilio usan Form Data y cómo procesarlo en FastAPI
- **`@app.on_event("startup")`:** Cómo inicializar recursos al arrancar el servidor antes de recibir peticiones
- **Structured Output con IA:** Cómo pedirle a Claude respuestas en formato JSON para procesarlas programáticamente
- **SQLite:** Diseño de base de datos relacional para persistir conversaciones y pedidos
- **Prompt Engineering avanzado:** Cómo construir system prompts que den contexto, personalidad y reglas de negocio a un agente de IA

---
<img width="738" height="1600" alt="Image" src="https://github.com/user-attachments/assets/dc618bfd-0eb7-49cb-8572-820e13d57199" />

<img width="738" height="1257" alt="Image" src="https://github.com/user-attachments/assets/aade1daa-474d-4745-8b94-77b351fa7388" />

<img width="738" height="1599" alt="Image" src="https://github.com/user-attachments/assets/77f1c3f9-bd8c-46d8-b5fa-db5f7297b39d" />


---

## 👨‍💻 Autor

Kevin González
[GitHub](https://github.com/kevinc-glz-snba)

---

## 📄 Licencia

MIT
