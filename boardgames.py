from bs4 import BeautifulSoup
import requests
import re
import smtplib
import configparser
import os.path

config = configparser.ConfigParser()
if os.path.isfile('dealfinder_custom.conf'):
    config.read('dealfinder_custom.conf')
else:
    config.read('dealfinder.conf')

smtpserver = config['SETTINGS']['smtpserver']
phonenumber = list(config.items('phonenumbers'))

class dealfinder():
    def __init__(self, phonenumber):
        self.header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0)'}
        self.redditurl = 'https://www.reddit.com/r/boardgamedeals/new/'
        self.timeout = 15
        self.matchregex = re.compile(r'(?P<recent>(\d+\s(hours|minutes)|1\sdays?)\sago)')
        self.smtpserver = smtpserver
        self.phonenumber = phonenumber

    def query(self, url):
        self.response = requests.get(url, headers=self.header, timeout=self.timeout)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.links = self.soup.find_all(['a'])
        self.deals = []
        self.count = 0
        #Wonky but it works
        for link in self.links:
            if self.count == 2:
                self.deals.append(link.text)
                self.count = 0 
            pass
            if self.count == 1:
                self.count +=1
                pass
            if self.matchregex.match(link.text):
                self.count += 1

    def sendemail(self):
        self.smtpobject = smtplib.SMTP(self.smtpserver, 25)
        for order, number in self.phonenumber:
            for deal in self.deals:
                print("Sending {0}".format(deal))
                self.smtpobject.sendmail(self.subject, str(number), deal.encode("ascii", 'ignore'))

if __name__ == "__main__":
    deal = dealfinder(phonenumber)
    deal.query(deal.redditurl)
    deal.subject = "Boardgame deal finder!"
    deal.sendemail()
