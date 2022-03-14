
import sqlite3
db = sqlite3.connect("onchecker.db")
db.execute("PRAGMA journal_mode = 'WAL'")
db.execute("""CREATE TABLE IF NOT EXISTS webcheck 
            (target TEXT,
            checktype TEXT,
            checked INTEGER DEFAULT 0,
            count INTEGER DEFAULT 0,
            trigger INTEGER DEFAULT 0,
            last TEXT DEFAULT 0,
            keyword TEXT,
            trycount INTEGER DEFAULT 0,
            trytrigger INTEGER DEFAULT 0)
            """)

select = -1
while select != 0:
    if select == -1:
        print("\n1. Add new website")
        print("2. List websites")
        print("3. Remove website")
        print("4. Clear saved information for each domain")
        print("0. Exit")
        select = int(input("Please select an option: "))

    if select == 1:
        print('For website text Checker write domain!keyword!checkskip! ex: https://www.google.com/!words here!1!')
        print('For website change checker write domain!checkskip ex: https://www.google.com/!0')
        print('For website uptime checker write domain!trytimes!checkskip ex: https://www.google.com/!5!0')
        print('For port checking write the fqdn or IP fqdn:port!trytimes!checkskip')
        p = input('0 to exit\n:')
        if p != str(0) and p != "":
            p = p.split("!")
            print(p)
            if ":" in p[0]:
                print("Adding to Port checker")
                db.execute("INSERT OR IGNORE INTO webcheck (target,trytrigger,trigger,checktype) VALUES(?, ?, ?, ?)",
                (p[0],p[1],p[2],"port"))
            elif len(p) == 4:
                print("adding to word search")
                db.execute("INSERT OR IGNORE INTO webcheck (target,keyword,trigger,checktype) VALUES(?, ?, ?,?)",
                (p[0],p[1],p[2],"word"))
            elif len(p) == 2:
                print("adding to web change")
                db.execute("INSERT OR IGNORE INTO webcheck (target,trigger,checktype) VALUES(?, ?, ?)",
                (p[0],p[1],"change"))
            elif len(p) == 3:
                print("addding to online checker")
                db.execute("INSERT OR IGNORE INTO webcheck (target,trytrigger,trigger,checktype) VALUES(?, ?, ?, ?)",
                (p[0],p[1],p[2],"online"))
            db.commit()
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
        print("word = Text Checker | change = Change Website | online = Uptime Checker")
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
