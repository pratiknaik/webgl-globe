import imaplib
import email
import json
import simplejson
import requests
import re

uid2 = ''
pwd2 = ''


emails = []
info = []
count = 0


conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)

conn.login(uid2, pwd2)

conn.select()

typ, data = conn.search(None, "ALL")

for num in data[0].split():
    typ, msg_data = conn.fetch(num, '(RFC822)') #Gets the content of each email.
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1])
            received = msg.get_all('Received-SPF')
            words = str(received)
            if words.find('neutral') != -1 or words.find('pass') != -1:
                result = re.search('client-ip=(.*);', words)
                if result is not None:
                    ip = result.group(1)
                    emails.append(ip)
                    count = count+1
                    print "Added ip " + str(count)

print emails
for i in emails:
    r = requests.get('http://www.freegeoip.net/json/'+ i)
    print r.status_code
    if r.status_code is 200:
        response = simplejson.loads(r.content)
        lat = response['latitude']
        lon = response['longitude']
        if lat is not 0 and lon is not 0:
            info.append(lat)
            info.append(lon)
            info.append(1)
            info.append(0)

highest_mag = 0
max_mag = 0.80
info_len = len(info)
for i in range(0, info_len, 4):
    for j in range(i+4, info_len, 4):
        if j+3 >= info_len:
            break
        if info[i] == info[j] and info[i+1] == info[j+1]:
            info[i+2] = info[i+2]+1
            if highest_mag < info[i+2]:
                highest_mag = info[i+2]
            del info[j:j+4]
            info_len = info_len - 4

for i in range(0, len(info), 4):
    info[i+2] = (info[i+2]*max_mag)/highest_mag


with open('coords.json', 'w') as outfile:
    json.dump(info, outfile)
try:
    conn.close()
except:
    pass
conn.logout()