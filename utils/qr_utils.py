import qrcode
import base64
from io import BytesIO

def generate_qr_base64(rid: str) -> str:
    """Generate QR code as base64 PNG string."""
    img = qrcode.make(rid)
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{qr_b64}"
