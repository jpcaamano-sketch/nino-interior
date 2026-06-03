import resend
from core.config import RESEND_API_KEY, FROM_EMAIL


def _send(params: dict):
    resend.api_key = RESEND_API_KEY
    return resend.Emails.send(params)


def enviar_reporte(nombre: str, correo: str, link: str, pdf_bytes: bytes):
    params = {
        "from": FROM_EMAIL,
        "to": [correo],
        "subject": f"Tu carta — Mi Niño Interior, {nombre}",
        "html": f"""
<div style="font-family:Georgia,serif;max-width:560px;margin:0 auto;padding:32px 24px;
            background:#faf6ee;border-radius:12px;">
  <h2 style="color:#d4a853;margin-bottom:16px;">Tu carta está lista, {nombre}</h2>
  <p style="color:#5a4a32;line-height:1.9;margin-bottom:16px;">
    Tu niño interior tiene algo que decirte. Lo encontrarás en el reporte adjunto.
  </p>
  <p style="color:#5a4a32;line-height:1.9;margin-bottom:16px;">
    También puedes acceder a él en línea en cualquier momento:
  </p>
  <div style="text-align:center;margin:32px 0;">
    <a href="{link}" style="background:#d4a853;color:#1a1208;padding:14px 36px;
       border-radius:6px;font-weight:700;font-size:16px;text-decoration:none;">
      Ver mi reporte →
    </a>
  </div>
  <p style="color:#9a8872;font-size:13px;text-align:center;font-style:italic;">
    Sanar no es olvidar lo que viviste. Es aprender a acompañarte como nadie pudo hacerlo entonces.
  </p>
</div>
""",
        "attachments": [{
            "filename": f"nino_interior_{nombre.lower().replace(' ', '_')}.pdf",
            "content": list(pdf_bytes),
        }],
    }
    return _send(params)
