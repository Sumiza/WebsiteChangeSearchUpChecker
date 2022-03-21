
import sqlite3
db = sqlite3.connect("onchecker.db")
db.execute("PRAGMA journal_mode = 'WAL'")
db.execute("""CREATE TABLE IF NOT EXISTS webcheck 
            (target TEXT,
            checktype TEXT,
            checked INTEGER DEFAULT 0,
            count INTEGER DEFAULT 1,
            trigger INTEGER DEFAULT 1,
            last TEXT DEFAULT 0,
            keyword TEXT,
            trycount INTEGER DEFAULT 0,
            trytrigger INTEGER DEFAULT 0)
            """)
def addinfo():
    print("Adding to database")
    db.execute("INSERT OR IGNORE INTO webcheck (target,checktype,trigger,keyword,trytrigger) VALUES(?, ?, ?, ?, ?)",
                (p["target"],p["checktype"],p["trigger"],p["keyword"],p["trytrigger"]))
    db.commit()
select = -1
while select != 0:
    p = {
        "target" : "",
        "checktype" : "",
        "trigger" : 1,
        "keyword" : "",
        "trytrigger" : 1
    }
    if select == -1:
        print("\n1. Add new website")
        print("2. List websites")
        print("3. Remove website")
        print("4. Clear saved information for each domain")
        print("0. Exit")
        select = int(input("Please select an option: "))

    if select == 1:
        print("\n1. Website Text Checker")
        print("2. Website Change Checker")
        print("3. Website Online Checker")
        print("4. Open Port Checker")
        print("0. Exit")
        select = int(input("Please select an option: "))
        if select == 1:
            print("\n"+"="*10+"Website Text Checker"+"="*10)
            p["checktype"] = "word"
            p["target"] = input("Target Domain, protocol(http or https required) ex: https://www.google.com/\n")
            p["keyword"] = input("Keyword, word or words to look for (case sensitive) ex: Words to look for\n")
            p["trigger"] = input("Check every runs, 1 is default at 60sec, ex: 1\n")
            yn = input(f"Check {p['target']} look for {p['keyword']} every {p['trigger']} Y/N" ).casefold()

        elif select == 2:
            p["checktype"] = "change"
            p["target"] = input("Target Domain, protocol(http or https required) ex: https://www.google.com/\n")
            p["trigger"] = input("Check every runs, 1 is default at 60sec, ex: 1\n")
            yn = input(f"Check {p['target']} every {p['trigger']} Y/N" ).casefold()
        
        elif select == 3:
            p["checktype"] = "online"
            p["target"] = input("Target Domain, protocol(http or https required) ex: https://www.google.com/\n")
            p["trigger"] = input("Check every runs, 1 is default at 60sec, ex: 1\n")
            p["trytrigger"] = input("Notify after how many tries come back as offline, ex: 1\n")
            yn = input(f"Check {p['target']} every {p['trigger']}, Notify after {p['trytrigger']} Y/N" ).casefold()

        elif select == 4:
            p["checktype"] = "port"
            p["target"] = input("Target IP or FQDN with port number ex: google.com:80 or 8.8.8.8:53\n")
            p["trigger"] = input("Check every runs, 1 is default at 60sec, ex: 1\n")
            p["trytrigger"] = input("Notify after how many tries come back as offline, ex: 1\n")
            yn = input(f"Check {p['target']} every {p['trigger']}, Notify after {p['trytrigger']} Y/N" ).casefold()

        if yn == "y":
            addinfo()
        select = -1

    elif select == 2:
        print("\n---Text Checker--")
        for i in db.execute("SELECT target,keyword,trigger FROM webcheck WHERE checktype = 'word'").fetchall():
            print(*i)
        print("\n---Change Website---")
        for i in db.execute("SELECT target,trigger FROM webcheck WHERE checktype = 'change'").fetchall():
            print(*i)
        print("\n---Uptime Checker---")
        for i in db.execute("SELECT target,trytrigger,trigger FROM webcheck WHERE checktype = 'online'").fetchall():
            print(*i)
        print("\n---Port Checker---")
        for i in db.execute("SELECT target,trytrigger,trigger FROM webcheck WHERE checktype = 'port'").fetchall():
            print(*i)
        select = -1

    elif select == 3:
        print("Select what domain to delete")
        print("word = Text Checker | change = Change Website | online = Uptime Checker | port = Port Checker")
        print("ex: online https://www.google.com")
        p = input('0 to exit\n')
        if p:
            p = p.split(" ")
            db.execute("DELETE FROM webcheck WHERE checktype = ? AND target = ?",(p[0],p[1]))
            db.commit()
        select = -1
    elif select == 4:
        print("Resetting all saved information for websites")
        db.execute('UPDATE webcheck SET last = 0, checked = 0, count = 0, trycount = 0')
        db.commit()
        select = -1
