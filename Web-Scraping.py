import os
import re
import json
import pandas as pd
from time import sleep
from urllib import request
import numpy as np
from googlesearch import search
from bs4 import BeautifulSoup as soup

###############################################################################
###############################################################################
################
## FUNCTIONS  ##
################

def decideTwitterSeparator(URL):
  if ('hashtag' in URL) | ('rupaulsdragrace' in URL): # If they posted a Tweet, extracts username from that.
    return None
  elif 'status' in URL: # Most likely no Twitter.
    return '/'
  else:
    return '?' # Usual separator for Twitter. 

def getUsernames(queen):

    instagramIndex = 26
    instagramURL = pd.Series(search(queen + ' drag queen instagram', num = 1, stop = 1, pause = 2))[0]
    instagramURLSubset = instagramURL[instagramIndex:]
    instagramSeparatorIndex = instagramURLSubset.find('/')
    instagramUsername = instagramURLSubset[:instagramSeparatorIndex]

    twitterIndex = 20
    twitterURL = pd.Series(search(queen + ' drag queen twitter', num = 1, stop = 1, pause = 2))[0]
    twitterURLSubset = twitterURL[twitterIndex:]
    twitterSeparator = decideTwitterSeparator(twitterURL)

    if twitterSeparator is None:
      twitterUsername = None
      print('|Queen: ' + queen + " |Instagram: " + str(instagramUsername) + "|Twitter: " + str(twitterUsername))
      return [instagramUsername, twitterUsername]

    twitterSeparatorIndex = twitterURLSubset.find(twitterSeparator)

    if twitterSeparatorIndex == -1:
      twitterSeparatorIndex = None

    twitterUsername = twitterURLSubset[:twitterSeparatorIndex]

    print('|Queen: ' + queen + " |Instagram: " + str(instagramUsername) + "|Twitter: " + str(twitterUsername))
    return [instagramUsername, twitterUsername]

def getFollowers(username, socialMedia):
  if socialMedia == 0:
    platform = "instagram"
  elif socialMedia == 1:
    platform = "twitter"
  else:
    print("Enter valid platform code. [0 - Instagram, 1 - Twitter]")
    return None

  if username is None:
    return None

  global runCount
  runCount += 1
  if runCount in np.round(np.linspace(0,260,12)):
    sleep(60)
  try:
    profileURL = "https://www."+platform+".com/"+username+"/"
    client = request.urlopen(profileURL)
    response = client.read()

    if platform == 'instagram':
      page_soup = soup(response).html.find('script', text = re.compile('window\._sharedData'))

      jsonSoup = json.loads(page_soup.string.partition('=')[-1].strip(' ;'))
      followerCount = jsonSoup['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
    elif platform == 'twitter':
      page_soup = soup(response).find('input',{'class':'json-data'})['value']

      jsonSoup = json.loads(page_soup)
      followerCount = jsonSoup['profile_user']['followers_count']
    else:
      print('Invalid platform.')
      followerCount = None
    client.close()
  except Exception as e:
    print(e)
    followerCount = None
        
  print(str(username) + ' has ' + str(followerCount) + ' ' + platform + ' followers!')
  return followerCount

###############################################################################
###############################################################################
###############################
## WEB-SCRAPING SOCIAL MEDIA ##
###############################
  
os.chdir('/Users/justinpimentel/Desktop/Drag Race Project/Data')

df = pd.DataFrame()
df['Queen'] = pd.read_csv('Queens.csv')['contestant'].drop_duplicates().reset_index(drop = True)
usernames = pd.Series([getUsernames(queen) for queen in df['Queen']])
df['Instagram'] = usernames.str[0]
df.loc[df['Queen'] == 'Rebecca Glasscock','Instagram'] = 'the_javier_rivera'
df.loc[df['Queen'] == 'Milan','Instagram'] = 'itsdwaynecooper'

df['Twitter'] = usernames.str[1]
df.loc[df['Queen'] == 'Milan','Twitter'] = 'itsdwaynecooper'
df.loc[df['Queen'] == 'Alisa Summers','Twitter'] = None
df.loc[df['Queen'] == "A'Keria C. Davenport",'Twitter'] = 'a_doublec_d'
df.loc[df['Queen'] == 'Jasmine Masters','Twitter'] = 'Jasminejmasters'

df.to_csv('Social-Media-Usernames.csv', index = False)
# =============================================================================

runCount = 0
df = pd.read_csv('Social-Media-Usernames.csv')

df['Instagram Followers'] = pd.Series([getFollowers(queen, 0) for queen in df['Instagram']])
df['Twitter Followers'] = pd.Series([getFollowers(queen, 1) for queen in df['Twitter']])

df = df[['Queen','Instagram','Instagram Followers', 'Twitter','Twitter Followers']]
df.to_csv('Social-Media-With-Followers.csv', index = False)

###############################################################################
###############################################################################
#############################
## WEB-SCRAPING (DRAG API) ##
#############################

def getInfo(queen):
    return [queen['name'],queen['quote'],queen['winner'],queen['missCongeniality']]
    
URL = "http://www.nokeynoshade.party/api/queens/all"
client = request.urlopen(URL)
response = client.read()
page_soup = json.loads(soup(response).p.text)

coStarViz = pd.DataFrame()
coStarViz['Queen'] = pd.Series(getInfo(queen)[0] for queen in page_soup)
coStarViz['Quote'] = pd.Series(getInfo(queen)[1] for queen in page_soup)
coStarViz['Winner?'] = pd.Series(getInfo(queen)[2] for queen in page_soup)
coStarViz['MissC?'] = pd.Series(getInfo(queen)[3] for queen in page_soup)

coStarViz.loc[coStarViz['Queen'] == "Victoria 'Porkchop' Parker", 'Queen'] = "Victoria (Porkchop) Parker"
coStarViz.loc[coStarViz['Queen'] == "Bebe Zahara Benet", 'Queen'] = "BeBe Zahara Benet"
coStarViz.loc[coStarViz['Queen'] == "Shangela Laquifa Wadley", 'Queen'] = "Shangela"
coStarViz.loc[coStarViz['Queen'] == "Mariah Balenciaga", 'Queen'] = "Mariah"
coStarViz.loc[coStarViz['Queen'] == "Stacey Lane Matthews", 'Queen'] = "Stacy Layne Matthews"
coStarViz.loc[coStarViz['Queen'] == "LaShauwn Beyond", 'Queen'] = "Lashauwn Beyond"
coStarViz.loc[coStarViz['Queen'] == "Madam LaQueer", 'Queen'] = "Madame LaQueer"
coStarViz.loc[coStarViz['Queen'] == "Willam Belli", 'Queen'] = "Willam"
coStarViz.loc[coStarViz['Queen'] == "Vivienne Piney", 'Queen'] = "Vivienne Pinay"
coStarViz.loc[coStarViz['Queen'] == "Detox Icunt", 'Queen'] = "Detox"
coStarViz.loc[coStarViz['Queen'] == "Roxxy Andrews", 'Queen'] = "Roxxxy Andrews"
coStarViz.loc[coStarViz['Queen'] == "Alaska Thunderfuck 5000", 'Queen'] = "Alaska"
coStarViz.loc[coStarViz['Queen'] == "April Carrion", 'Queen'] = "April Carrión"
coStarViz.loc[coStarViz['Queen'] == "Trinity K Bonet", 'Queen'] = "Trinity K. Bonet"
coStarViz.loc[coStarViz['Queen'] == "Katya Zamolodchikova", 'Queen'] = "Katya"
coStarViz.loc[coStarViz['Queen'] == "Nina Bo'Nina Brown", 'Queen'] = "Nina Bo'nina Brown"
coStarViz.loc[coStarViz['Queen'] == "Shea Coulee", 'Queen'] = "Shea Couleé"
coStarViz.loc[coStarViz['Queen'] == "Dusty Rae Bottoms", 'Queen'] = "Dusty Ray Bottoms"
coStarViz.loc[coStarViz['Queen'] == "Monet X Change", 'Queen'] = "Monét X Change"
coStarViz.loc[coStarViz['Queen'] == "Jamyes Mansfield", 'Queen'] = "Jaymes Mansfield"

coStarViz.to_csv('coStarViz.csv', index = False)