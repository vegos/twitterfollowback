# -*- coding: utf-8 -*-
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import tweepy
from tweepy import *
import time
import numpy as np
import mysql.connector
from datetime import date, datetime, timedelta
import csv
print "---------------------- GetFollowerts -----------------------"
print time.strftime("%d/%m/%Y %H:%M")     
print "Getting followers"
username = '<username>'
#config.py contains your twitter's API consumer_key, consumer_secret, access_key, and access_secret
config = {}
execfile("./config.py", config)
fh_output = open("/tmp/followerscount.txt", 'w')

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(config["CONSUMER_KEY"], config["CONSUMER_SECRET"])
    auth.set_access_token(config["ACCESS_KEY"], config["ACCESS_SECRET"])
    api = tweepy.API(auth)
    data = api.get_user(username)
    followers = []
    total = 0
    for user in tweepy.Cursor(api.followers, screen_name=username, count = 200).items():
        num = int(user.followers_count)
        total = total + num
        fh_output.write(user.screen_name +','+user.name+'\n')
         
fh_output.close()

cnx = mysql.connector.connect(user='<mysql username>', password='<mysql password>',
                              host='<mysql ip>',
                              database='twitter')

f = open('/tmp/followerscount.txt','r')
reader = csv.reader(f)

print "Checking for new followers, follow them, add them to db and send them message"

totalfollowers = 0
newfollowers = 0
newnames = ""
newids = ""

for row in reader:
   name = row[0]
   username = row[1].encode("utf-8").replace("'","")
   query = "SELECT screen_name FROM twitterfollowers WHERE screen_name = '%s'" % name
   cur = cnx.cursor(buffered=True)
   cur.execute(query)
   result = cur.fetchall()
   totalfollowers += 1
   if cur.rowcount == 0:
     ts = time.strftime('%Y-%m-%d %H:%M:%S')
     username = username.decode('utf-8').encode('utf-8')
     query = "INSERT INTO twitterfollowers (screen_name, datetime, user_name) VALUES ('%s', '%s', '%s')" % (name,ts,username)
     cur.execute(query)
     cnx.commit()
     newfollowers += 1
     newnames += username+" "
     newids += name+" "
     api.create_friendship(screen_name = name)
     text="<custom message to send when following back>"
     x = api.send_direct_message(name,text=text)
     api.destroy_direct_message(x.id)
cnx.close()

print "Total followers:",totalfollowers
if newfollowers != 0:
  print "New followers (send messages/follow):",newfollowers
  print "New followers names:",newnames
  print "New followers ids:",newids
else:
  print "No new followers"
  
print "Done"
