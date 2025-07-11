import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Configuración (ajusta según tu proveedor)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = "claudiocn089@gmail.com"
PASSWORD = "xevmfxldkjfvvzzs"
DESTINATARIO = "claudiocn089@gmail.com"

def enviar_email(asunto, cuerpo, adjunto=None):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = DESTINATARIO
    msg['Subject'] = asunto

    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 send_email.py 'Asunto' archivo.txt")
        sys.exit(1)

    asunto = sys.argv[1]
    archivo = sys.argv[2]

    with open(archivo, encoding="utf-8") as f:
        cuerpo = f.read()

    enviar_email(asunto, cuerpo)
