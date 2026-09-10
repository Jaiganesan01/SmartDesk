import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import config
import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_support_email(recipient_email: str, subject: str, body: str) -> str:
    db_configs = database.get_email_configs()
    
    smtp_host = db_configs.get('_smtp_host', '').strip() or config.SMTP_HOST
    smtp_port_val = db_configs.get('_smtp_port', '').strip() or str(config.SMTP_PORT)
    smtp_port = int(smtp_port_val) if smtp_port_val.isdigit() else 587
    smtp_user = db_configs.get('_smtp_user', '').strip() or config.SMTP_USER
    smtp_password = db_configs.get('_smtp_password', '').strip() or config.SMTP_PASSWORD
    smtp_sender = db_configs.get('_smtp_sender', '').strip() or smtp_user or config.SMTP_SENDER
    
    if not all([smtp_host, smtp_user, smtp_password]):
        logger.info('SMTP configuration not fully set in UI or .env. Falling back to simulated email routing.')
        return 'Simulated'
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_sender
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        logger.info(f"Connecting to SMTP server {smtp_host}:{smtp_port}...")
        
        if smtp_port == 465:
            server_conn = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server_conn = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            
        with server_conn as server:
            if smtp_port != 465:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_sender, recipient_email, msg.as_string())
            
        logger.info(f"Email successfully delivered to {recipient_email}")
        return 'Sent'
    except Exception as e:
        logger.error(f"Error during SMTP email transmission to {recipient_email}: {e}")
        return 'Failed'
