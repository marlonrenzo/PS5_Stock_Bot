import smtplib
from email.message import EmailMessage

u = "marlon.automated.message@gmail.com"
p = "keeujwoxalxeotzd"


def send_message(subject, body, recipient):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = recipient
    msg['from'] = u

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(u, p)
    server.send_message(msg)
    print("Sending automated message...")
    server.quit()


def main():
    send_message("PS5 stock update", "No new PS5's available",
                 "7782313497@txt.freedommobile.ca")


if __name__ == '__main__':
    main()
