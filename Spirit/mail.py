import smtplib

class mail:
    def __init__(self, sender: str, password: str, server: str="smtp.gmail.com", port: int=465):
        self.server = server
        self.port = port
        self.sender = sender
        self.__password = password

        self.__serverConn = smtplib.SMTP_SSL(self.server, self.port)
        self.__serverConn.login(self.sender, self.__password)

    def message(self, sender: str, recipients: [], subject: str, message: str, subType: str="text/plain") -> bool:
        msg = f"From: {sender}\r\nTo: {','.join(recipients)}\r\nSender: Spirit\r\nContent-Type: {subType}\r\nSubject: {subject}\r\n\r\n{message}"
        try:
            self.__serverConn.sendmail(sender, recipients, msg)
            return True
        except Exception as e:
            return False