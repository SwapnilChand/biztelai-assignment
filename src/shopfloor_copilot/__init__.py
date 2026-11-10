import os
import socket


def lan_ip() -> str:
    """The address other devices on the same Wi-Fi can reach this laptop on."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no packet is sent, this only picks the route
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    import qrcode
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    # inside Docker the container IP is useless to a phone, so allow an override
    url = os.getenv("PUBLIC_URL") or f"http://{lan_ip()}:{port}"
    print(f"\nOpen on your phone (same Wi-Fi): {url}\n")
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.print_ascii(invert=True)
    uvicorn.run("shopfloor_copilot.server:app", host="0.0.0.0", port=port)
