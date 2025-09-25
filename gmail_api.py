import smtplib 
import email.message

def enviar_email():
    corpo_email = """
    <p>Olá Jéssica</p>
    <p>Segue meu email automatico</p>
    """
    msg = email.message.Message()
    msg['Subject'] = "Assunto"
    msg['From'] = 'umidadeprojetointegradorsenai@gmail.com'
    msg['To'] = 'umidadeprojetointegradorsenai@gmail.com'
    password = 'qmrcthjzlmwzrxvh'
    msg.add_header('Contect-Type', 'text/html')
    msg.set_payload(corpo_email)
    
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login(msg['From'],password)
    s.sendmail(msg['From'],[msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')
    
if __name__ == "__main__":
    enviar_email()