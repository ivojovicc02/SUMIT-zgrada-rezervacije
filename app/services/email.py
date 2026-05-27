from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_reservation_confirmation(
    email: str,
    first_name: str,
    space_name: str,
    start_time: datetime,
    end_time: datetime,
    total_price: float,
    reservation_id: int,
):
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2c3e50;">Potvrda rezervacije — SUMIT centar</h2>
        <p>Poštovani/a <strong>{first_name}</strong>,</p>
        <p>Vaša rezervacija je uspješno kreirana. Detalji:</p>

        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr style="background: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Prostor</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{space_name}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Datum i vrijeme</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">
                    {start_time.strftime("%d.%m.%Y %H:%M")} — {end_time.strftime("%H:%M")}
                </td>
            </tr>
            <tr style="background: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Ukupna cijena</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{total_price:.2f} KM</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Broj rezervacije</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">#{reservation_id}</td>
            </tr>
        </table>

        <p>U slučaju pitanja kontaktirajte nas na <a href="mailto:info@sumit.ba">info@sumit.ba</a>.</p>
        <p style="color: #7f8c8d; font-size: 12px;">SUMIT centar — Vaš poslovni prostor</p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Potvrda rezervacije #{reservation_id} — SUMIT centar",
        recipients=[email],
        body=body,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_reservation_reminder(
    email: str,
    first_name: str,
    space_name: str,
    start_time: datetime,
):
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2c3e50;">Podsjetnik — SUMIT centar</h2>
        <p>Poštovani/a <strong>{first_name}</strong>,</p>
        <p>Podsjećamo vas da sutra imate rezervaciju:</p>

        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr style="background: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Prostor</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{space_name}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Datum i vrijeme</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">
                    {start_time.strftime("%d.%m.%Y u %H:%M")}
                </td>
            </tr>
        </table>

        <p>Vidimo se sutra!</p>
        <p style="color: #7f8c8d; font-size: 12px;">SUMIT centar — Vaš poslovni prostor</p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Podsjetnik za sutrašnju rezervaciju — SUMIT centar",
        recipients=[email],
        body=body,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_cancellation_email(
    email: str,
    first_name: str,
    space_name: str,
    start_time: datetime,
    reservation_id: int,
):
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #e74c3c;">Otkazivanje rezervacije — SUMIT centar</h2>
        <p>Poštovani/a <strong>{first_name}</strong>,</p>
        <p>Vaša rezervacija je otkazana:</p>

        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr style="background: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Prostor</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{space_name}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Datum i vrijeme</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">
                    {start_time.strftime("%d.%m.%Y u %H:%M")}
                </td>
            </tr>
            <tr style="background: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Broj rezervacije</strong></td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">#{reservation_id}</td>
            </tr>
        </table>

        <p>Za više informacija kontaktirajte nas na 
        <a href="mailto:info@sumit.ba">info@sumit.ba</a>.</p>
        <p style="color: #7f8c8d; font-size: 12px;">SUMIT centar — Vaš poslovni prostor</p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Otkazivanje rezervacije #{reservation_id} — SUMIT centar",
        recipients=[email],
        body=body,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)