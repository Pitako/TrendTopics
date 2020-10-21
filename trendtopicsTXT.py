#!/usr/bin/env python
#coding: utf-8

# In[2]:


import sys
import tweepy
import json
from datetime import datetime

#import mysql.connector
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# In[3]:


#Autenticacoes
consumer_key = 'jULJjwOSBmILsAaIWRSV6BkTM'
consumer_secret = 'ZUGIjz07rSYaug3ltxUbEeMNa3dD6yYs6E9zEAdPd1nzcXId2n'
access_token = '343335743-RpyWTzbqaxzBCoMZBjtkN2TIMmhVYZcCPyHe9lda'
access_token_secret = 'YZJbm9y1qABs6yurUo5sblzoC1ICy7SnqZMDRwhggcFfb'


# In[4]:


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
 
# O Yahoo! Where On Earth ID para o Brasil e 23424768.
# Veja mais em https://dev.twitter.com/docs/api/1.1/get/trends/place e http://developer.yahoo.com/geo/geoplanet/
BRAZIL_WOE_ID = 23424768
 
# brazil_trends = api.trends_place(BRAZIL_WOE_ID)
 
# trends = json.loads(json.dumps(brazil_trends, indent=1))
 
# for trend in trends[0]["trends"]:
# 	print (trend["name"]+' '+str(trend["tweet_volume"]))
    


# In[ ]:





# In[5]:


# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="root",
#   database="twitterreacttv"
    
# )

# print(mydb)

# mycursor = mydb.cursor()


# In[6]:


# mycursor = mydb.cursor()

# sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# val = ("John", "Highway 21")
# mycursor.execute(sql, val)

# mydb.commit()


# In[9]:


# now = datetime.now()

# brazil_trends = api.trends_place(BRAZIL_WOE_ID) 
# trends = json.loads(json.dumps(brazil_trends, indent=1))

# for trend in trends[0]["trends"]:
#     val = now.strftime("%d/%m/%Y %H:%M:%S") + ";" + trend["name"] + ";" + str(trend["tweet_volume"]);
                
#     print(val)


# In[ ]:





# In[18]:


outputFile = 'trendtopics.txt'


# In[23]:


while True:    
    now = datetime.now()
    if ( int(now.strftime('%M'))%5==0.0 ):
        try:
            brazil_trends = api.trends_place(BRAZIL_WOE_ID) 
            trends = json.loads(json.dumps(brazil_trends, indent=1))

            for trend in trends[0]["trends"]:
                #print (trend["name"]+' '+str(trend["tweet_volume"]))            
                #sql = 'INSERT INTO trendtopics (data, texto, volume) VALUES (%s, %s, %s)'
                val = now.strftime("%d/%m/%Y %H:%M:%S") + ";" + trend["name"] + ";" + str(trend["tweet_volume"]) + '\n';
                
                #mycursor.execute(sql, val)
                
                file = open(outputFile, mode='at+')
                #print(val)                
                
                file.write(val)
                file.close()

            #print (now.strftime("%d/%m/%Y %H:%M:%S"))
            #mydb.commit()
            time.sleep(65)
        except Exception as e:
            print(e)
            print()
            continue
            

        





