from time import sleep, time
from requests import get, head
from bs4 import BeautifulSoup
from threading import Thread
from difflib import ndiff
from apisender import send
import socket
import sqlite3


class Parsedb(object):

    def __init__(self,full:tuple) -> None:
        self.target = full[0]
        self.checktype = full[1]
        self.checked = full[2]
        self.count = full[3]
        self.trigger = full[4]
        self.last = full[5]
        self.keyword = full[6]
        self.trycount = full[7]
        self.trytrigger = full[8]
        self.message = ""
        self.title = ""
        self.statuscode = 0
        self.new = ""

    def getwebsite(self) -> None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        try:
            if self.checktype == "word" or self.checktype == "change":
                r = get(self.target,headers=headers,timeout=5)
                soup = BeautifulSoup(r.text,'html.parser')
                if soup.title:
                    self.title = soup.title.string
                else:
                    self.title = self.target
                self.new = "".join([s for s in soup.get_text().strip().splitlines(True) if s.strip()])
                self.statuscode = r.status_code                  
            elif self.checktype == "online":
                r = head(self.target,headers=headers,timeout=5)
                self.statuscode = r.status_code
        except:
            self.statuscode = 404

    def getport(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
                so.settimeout(5)
                target = self.target.split(":")
                self.statuscode = so.connect_ex((socket.gethostbyname(target[0]), int(target[1])))
                if self.statuscode == 0:
                    self.new = "Port Open"
                else:
                    self.new = "Port Closed"
        except:
            self.new = "Error"

    def checkport(self):
        self.getport()
        if self.statuscode == 0:
            self.message = f"Port is OPEN after {int(time())-int(self.checked)} seconds"
            self.trycount = 0
        else:
            self.message = "Port is Closed"
            self.trycount += 1

        if self.new != self.last:
            if self.trycount == self.trytrigger or self.trycount == 0:
                self.sendmess()
        elif self.trycount == 0 or self.trycount > self.trytrigger:
            return
        db.execute("UPDATE webcheck SET last = ?, trycount = ?, checked = ?, count = 1 WHERE target = ? AND checktype = 'port'",
                    (self.new,self.trycount,int(time()),self.target))


    def websitetextcheck(self) -> None:
        self.getwebsite()
        if 400 >= self.statuscode >= 200:
            self.message = "- Not Found"
            if self.keyword in self.new:
                self.message = "- Found"
            if self.message != self.last:
                self.sendmess()
            db.execute("UPDATE webcheck SET last = ?, checked = ?, count = 1 WHERE target = ? AND checktype = 'word'",
                        (self.message,int(time()),self.target))

    def websitechange(self) -> None:
        self.getwebsite()
        if 400 >= self.statuscode >= 200:
            if self.last != self.new:
                diff = ndiff(self.last.splitlines(), self.new.splitlines())
                self.message = [l for l in diff if l.startswith("+ ") or l.startswith("- ")]
                self.message = '\n'.join(self.message)
                if self.checked == 0:
                    self.message = "Website Added"
                self.sendmess()
            db.execute("UPDATE webcheck SET last = ?, checked = ?, count = 1 WHERE target = ? AND checktype = 'change'",
                        (self.new,int(time()),self.target))
    
    def websitestatus(self) -> None:
        self.getwebsite()
        if 400 >= self.statuscode >= 200:
            self.message = f"Is ONLINE after {int(time())-int(self.checked)} seconds"
            self.trycount = 0
        else:
            self.trycount += 1
            self.message = "Is OFFLINE"

        if str(self.statuscode) != self.last:
            if self.trycount == self.trytrigger or self.trycount == 0:
                self.sendmess()
        elif self.trycount == 0 or self.trycount > self.trytrigger:
            return
        db.execute("UPDATE webcheck SET last = ?, trycount = ?, checked = ?, count = 1 WHERE target = ? AND checktype = 'online'",
                    (self.statuscode,self.trycount,int(time()),self.target))

    def sendmess(self):
        """
            Connect whatever API to send messages
        """
        if self.checktype == 'word':
            self.mess = f"Website: {self.target}\n{self.title}\n{self.keyword} {self.message}\n"+"="*80
            subject = "Website Word Finder"
        elif self.checktype == 'change':
            self.mess = f"Website: {self.target}\n{self.title}\n{self.message}\n"+"="*80
            subject = "Website Changed"
        elif self.checktype == 'online':
            self.mess = f"Website: {self.target}\n{self.message}\nStatus Code:{self.statuscode}\n"+"="*80
            subject = "Website Online Checker"
        elif self.checktype == 'port':
            self.mess = f"Port: {self.target}\n{self.message}\n"+"="*80
            subject = "Port Checker"
        send(bodytext=self.mess,subject=subject,sendby="discord")
        print(subject,"\n",self.mess)

    def runornot(self) -> bool:
        if self.count >= self.trigger:
            # print("returning true for ",self.target,self.count,self.trigger)
            return True
        else:
            # print("returning false for ",self.target,self.count,self.trigger)
            db.execute("UPDATE webcheck SET count = ? WHERE target = ? AND checktype = ?",
                        (self.count+1,self.target,self.checktype))
            return False

    def typeselect(self) -> None:
        if self.runornot():
            if self.checktype == 'word':
                self.websitetextcheck()
            elif self.checktype == 'change':
                self.websitechange()
            elif self.checktype == 'online':
                self.websitestatus()
            elif self.checktype == 'port':
                self.checkport()

def amionlinedns(hostlist:list = ["1.1.1.1","8.8.8.8","9.9.9.9"]):
    """
    Returns True if can connect to any of the dns server in hostlist.
    Returns False if cant connect.
    Args:
        hostlist:list default is cloudflare, google, quad9
    """
    for host in hostlist:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.settimeout(5)
            response = so.connect_ex((host,53))
            if response == 0:
                return True
    return False

def checkall(waitsleep:int = 60,threading:bool = False):
    threads = []
    starttime = time()
    if amionlinedns():
        for i in db.execute("SELECT DISTINCT checktype from webcheck").fetchall():
            for j in db.execute(f"SELECT * FROM webcheck WHERE checktype = '{i[0]}'").fetchall():
                check = Parsedb(j)
                if threading:
                    t = Thread(target=check.typeselect)
                    threads.append(t)
                    t.start()
                else:
                    check.typeselect()
        if threading:
            for i in threads:
                i.join()
        db.commit() 
    db.close()
    sleeptimer(starttime,waitsleep)
    # print(time()-starttime)

def sleeptimer(starttime:float,stimer:float):
    stimer = starttime-time()+stimer
    if stimer > 0:
        sleep(stimer)

if __name__ == '__main__':
    while True:
        db = sqlite3.connect("onchecker.db",check_same_thread=False)
        db.execute("PRAGMA journal_mode = 'WAL'")
        checkall()
