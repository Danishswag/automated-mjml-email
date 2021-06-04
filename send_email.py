import json
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import pystache


def get_settings(f_settings: Path = Path() / 'settings.json') -> dict:
    """Read in the Gmail username/password to use"""
    print('Getting Gmail credentials')
    with f_settings.open() as settings_json:
        settings = json.load(settings_json)

    return settings


def send_email_handler() -> None:
    """General handler function for sending the email"""
    print('Hi friend!')
    credentials = get_settings()

    # Set up gmail info, modifying for our "real" gmail account
    gmail_username = credentials['gmail_user']
    gmail_password = credentials['gmail_pass']
    port = 465
    gmail_smtp_url = 'smtp.gmail.com'

    # Create a secure SSL context so you know your email is encrypted on the way to the server
    context = ssl.create_default_context()

    # read in the email template, remember to use the compiled HTML version!
    email_template = (Path() / 'email_template' / 'email_template.html').read_text()

    # Pass in values for the template using a dictionary
    template_params = {'first_name': 'JustJensen'}

    # Get emails from the settings.json
    receiver_email = "justjensen.real.email@gmail.com"
    sender_email = "justjensen.real.email@gmail.com"

    # Creating the email
    message = MIMEMultipart('mixed')
    message['Subject'] = 'We know where the hobbits are going!'
    message["From"] = sender_email
    message["To"] = receiver_email

    # First get the logo and prepare it for the attachment
    logo_path = Path() / 'email_template' / 'ghost-blog-logo.png'
    logo = logo_path.open()
    logo_img = MIMEImage(logo_path.read_bytes())
    logo.close()
    logo_img.add_header('Content-ID', f'<{logo_path.name}>')

    # Now adjust the pystache dictionary to handle both variables
    template_params = {'first_name': 'JustJensen',
                       'logo': logo_path.name}
    final_email_html = pystache.render(email_template, template_params)
    message.attach(MIMEText(final_email_html), 'html')
    message.attach(logo_img)

    # Preparing the attachment
    pdf_to_attach = Path() / 'Parking-Violations-Issued-in-January-2020.pdf'
    attachment_part = MIMEBase("application", "octet-stream")
    attachment_part.set_payload(pdf_to_attach.read_bytes())
    encoders.encode_base64(attachment_part)

    # Set up the key value pair
    attachment_part.add_header(
        'Content-Disposition',
        f'attachment; filename= {pdf_to_attach.name}'
    )

    message.attach(attachment_part)

    # Send the same test email as before, but through gmail to a "real" gmail account!
    with smtplib.SMTP_SSL(gmail_smtp_url, port, context=context) as gmail_server:
        gmail_server.login(gmail_username, gmail_password)
        gmail_server.sendmail(
            gmail_username, receiver_email, message.as_string()
        )


if __name__ == "__main__":
    send_email_handler()
