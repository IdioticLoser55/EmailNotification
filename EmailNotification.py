import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import json
import discord

class EmailServerDetails:
    def __init__(self, username, password, imapServer, port):
        self.username = username
        self.password = password
        self.imapServer = imapServer
        self.port = port
        
    def __iter__(self):
        yield from {
            "username": self.username,
            "password": self.password,
            "imapServer": self.imapServer,
            "port": self.port
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def toJson(self):
        return self.__str__()

    @staticmethod
    def fromJson(jsonDict):
        return EmailServerDetails(jsonDict['username'], 
            jsonDict['password'], 
            jsonDict['imapServer'], 
            jsonDict['port'])

esd = EmailServerDetails.fromJson(json.loads(open("/home/idiot/EmailNotification/BlueshellMail.json").read()))

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

imap = imaplib.IMAP4_SSL(esd.imapServer, esd.port)
imap.login(esd.username, esd.password)

status, messages = imap.select("INBOX")
N = 1
messages = int(messages[0])

for i in range(messages, messages - N, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)
            
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decdoe(encoding)
            
            date, encoding = decode_header(msg["Delivery-date"])[0]
            if isinstance(date, bytes):
                date = date.decode(encoding)
                


def notify(subject, From):
    # opens a file as readonly to obtain the token.
    token = open("/home/idiot/HovelHelper/token.txt", "r").read()
    
    # Stars the discord client
    client = discord.Client()
    
    @client.event  # event decorator/wrapper. More on decorators here: https://pythonprogramming.net/decorators-intermediate-python-tutorial/. Basically makes the following function as if it has been declared inside of the function event.
    async def on_ready():  # method expected by client. This runs once when connected
        print(f'We have logged in as {client.user}')  # notification of login.
    
        # Sends a simple startup message.
        channel = client.get_guild(909496426390753280).get_channel(1007247309815435317)
        if(channel != None):
            await channel.send(f"@everyone\n```\n"
                    + From + ":\n" + subject + "```")
        
        await client.close()
            
    client.run(token)


oldDate = open("/home/idiot/EmailNotification/oldDate.txt", "r").read()
if(oldDate != date):
    notify(subject, From)
    open("/home/idiot/EmailNotification/oldDate.txt", "w").write(date)
