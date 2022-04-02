#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 14:40:20 2021

@author: OldMac
"""
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailHandling:
   
    
    def __init__(self,text):
        
        self.smtp_server = "smtp.gmail.com"
        self.port = 465  # For starttls
        
        self.sender_email = "tobiastradinginfo@gmail.com"
        self.receiver_email = 'tellmiger@gmail.com'
        
        self.password = 'Vi30Vi07An!e'
    
        # Create a secure SSL context
        self.context = ssl.create_default_context()
        
        #send the mail
        self.sendmail(text)
        
    def sendmail(self,text):
                # Try to log in to server and send email
        try:            
            message  =self.generateMessage(text)
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=self.context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(
                    self.sender_email, self.receiver_email, message.as_string()
                )
        except Exception as e:
            # Print any error messages to stdout
            print(e)
    
    def generateMessage(self, text):
        message = MIMEMultipart("alternative")
        message["Subject"] = "Trading Update of TobisTradingBot"
        message["From"] = self.sender_email
        message["To"] = self.receiver_email
        
        part1 = MIMEText(text, "plain")
        
        message.attach(part1)
        
        return message
    
