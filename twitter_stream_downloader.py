import json
import os
from pymongo import MongoClient
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from tweepy import OAuthHandler
import tweepy
from tweepy.streaming2 import Stream, StreamListener
import urllib


consumer_key='KIWRd2XJqG6416WwmvMCCiZ3U'
consumer_secret='Y1dRPnfcvToGnftqGlyiBdeobHEErvmQnukigylAY6BvuQzxrE'
access_token_key='92787945-80YD0wq09a4Ln4BgM08BBrK2fpIqQakIZ4fZlr7S3'
access_token_secret='JJZXm8iwXJg5BIkkFSWJAUiajM8sx4QpZKtTiN3N6sj1l'
localDir = './'
            
def process_or_store(tweet):
#    keyword_tweet = json.dumps(tweet)
    tweet_id = tweet['id_str']
    screen_name = tweet['user']['screen_name']    
    seedUrl='https://mobile.twitter.com/'+screen_name+'/status/'+tweet_id
    searchLink(seedUrl,localDir)
    tweet['video_name']=filename
    collection.insert_one(tweet)


def GetVideoFileNameFromURL(url):
    outputFileName = url.split('/')[-1]
    return outputFileName
	

def GetVideoFromURL(url, fileName):
    print "Processing: " + url
    try:
        urllib.urlretrieve(url, fileName)
        print 'Saving : %s ...'%fileName
        return True
    except:
        print "Video: Failed to save URL: " + url
        return False

def searchLink(seedUrl, localDir):
    videofolder = localDir + 'Video/instanttweets/'
    if not os.path.exists(videofolder):
        os.makedirs(videofolder)
    global browser
    browser = webdriver.Chrome("./chromedriver")
    browser.get(seedUrl)
    time.sleep(2)
    browser.find_element_by_xpath("//a[contains(@class,'_1_aozdMe')]").click()
    time.sleep(1)
    videosrc = browser.find_element_by_xpath("//source[contains(@type,'video/mp4')]").get_attribute('src')
    browser.quit()
    global filename
    filename=GetVideoFileNameFromURL(videosrc)
    videoFile = videofolder + filename
    GetVideoFromURL(videosrc,videoFile)


class MyListener(StreamListener):

    def on_data(self,data):
        try:
            
            tweet = json.loads(data)
            process_or_store(tweet)
            #collection.insert_one(tweet)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            browser.quit()
        return True

    def on_error(self,status):
        print(status)
        return True


if __name__ == "__main__":
                      
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token_key, access_token_secret)
        api = tweepy.API(auth)

        client = MongoClient('localhost',27017)
        db = client.TwitterDB
        collection = db.instant_tweets
        
        twitter_stream=Stream(auth,MyListener(),proxy='127.0.0.1:1080')
        twitter_stream.filter(track=['video'])

    except tweepy.error.TweepError as e:
        print("Unable to authenticate", e)
        browser.quit()
    except NoSuchElementException:
        print "can't find videosrc"
        browser.quit()
