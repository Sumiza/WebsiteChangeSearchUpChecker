import json
import requests

def smtp2go(**kwargs) -> str:
  header = {'Content-type': 'application/json'}
  authkey = readfile("smtp2go")
  data = {
  "api_key": authkey,
  "sender": kwargs['fromid'],
  "to": [kwargs['toid']],
  "subject": kwargs['subject'],
  "text_body": kwargs['bodytext']
  }
  return requests.post("https://api.smtp2go.com/v3/email/send",json.dumps(data),headers=header)

def discord(**kwargs) -> str:
  authkey = readfile("discord")
  webheader = {"Content-Type": "application/json; charset=utf-8"}
  data= {"content":f"{kwargs['bodytext']}","username": f"{kwargs['subject']}"}
  return requests.post("https://discord.com/api/webhooks/"+authkey+"?wait=true",headers=webheader,data=json.dumps(data))

def mailjet(**kwargs) -> str:
  header = {'Content-type': 'application/json'}
  auth = readfile("mailjet")
  data = {
  'Messages': [{
          "From": {
              "Email": kwargs['fromid'],
              "Name": kwargs['fromname']
          },
          "To": [{
                  "Email": kwargs['toid'],
                  "Name": kwargs['toname']
              }],
          "Subject": kwargs['subject'],
          "TextPart": kwargs['bodytext'],
          "HTMLPart": kwargs['bodyhtml']
          }]}
  return requests.post("https://api.mailje5t.com/v3.1/send",json.dumps(data),headers=header,auth=auth)

def readfile(name):
  with open("apisender.json") as api:
    api = json.loads("".join(api.readlines()))
    if name == "discord" or name == "smtp2go":
      return api[name]["authkey"]
    elif name == "mailjet":
      return api[name]["authuser"],api[name]["authpass"]
    elif name == "fromid":
      return api["default"]["fromid"]
    elif name == "toid":
      return api["default"]["toid"]

def send(fromid:str="",toid:str="",subject:str="",fromname:str="",toname:str="",bodytext:str="",bodyhtml:str="",sendby:str=""):
  """
  args:
  fromid:   From email/smsnr/discordname
  toid:     To email/smsnr
  subject:  Email subject
  fromname: Email From name
  toname:   Email To name
  bodytext: Message email/sms/discord
  bodyhtml: Message email/discord?
  """
  if fromid == "":
    fromid = readfile("fromid")
  if toid == "":
    toid = readfile("toid")

  try:
    return sendbywho(fromid=fromid,
                      toid=toid,
                      subject=subject,
                      fromname=fromname,
                      toname=toname,
                      bodytext=bodytext,
                      bodyhtml=bodyhtml,
                      sendby=sendby)
  except:
    return "Failed to send"
    
def sendbywho(**kwargs):
  if kwargs['sendby'] == "discord":
    a = discord(**kwargs)
  elif kwargs['sendby'] == "smtp2go":
    a = smtp2go(**kwargs)
  elif kwargs['sendby'] == "mailjet":
    a = mailjet(**kwargs)
  else:
    pass
  return a.text
