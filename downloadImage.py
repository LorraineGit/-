import os

from bs4 import BeautifulSoup
#import mechanize
#import re
import Queue
import urllib

from selenium import webdriver
import socket
#socket.setdefaulttimeout(30)

def GetImageFromURL(url, fileName):
    # download images using url, and save it as fileName
    print "Processing: " + url
    try:
        urllib.urlretrieve(url, fileName)
        return True
    except:
        print "IMAGE: Failed to save URL: " + url
        return False

def GetImgFileNameFromURL(url):
    outputFileName = url.split('/')[-1] + '.jpg'
    return outputFileName
    
def GetHtmlFileNameFromURL(url):
    outputFileName = url
    outputFileName = outputFileName.replace(":", "")
    outputFileName = outputFileName.replace("//", "_")
    outputFileName = outputFileName.replace("/", "_")
    outputFileName = outputFileName.replace("\\", "_")
    outputFileName = outputFileName.replace("?", "_")
    return outputFileName

def SaveHtml(content, fileName):
    fp = open(fileName, 'w+')
    #fp.write(content.encode("ascii","replace")) #ignore
    fp.write(content.encode("GBK","replace"))
    fp.close()

def searchLink(seedUrl, localDir):
    # the main function
    # staring from seedUrl, parse the webpage and extract the links to other pages and image urls

    links = dict()
    imgUrls = dict()
    nLink = 0
    nImg = 0
    
    nLink = nLink + 1
    links[seedUrl] = nLink
    queue = Queue.Queue()
    queue.put( (seedUrl,0) )
    
    """
    browser = mechanize.Browser()
    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots( False )
    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    browser.set_handle_refresh(False)
    """
    browser = webdriver.Chrome('./chromedriver')
    
    txtfolder = localDir + 'Text' + '/'
    if not os.path.exists(txtfolder):
        os.makedirs(txtfolder)

    imgfolder = localDir + 'Image' + '/'
    if not os.path.exists(imgfolder):
        os.makedirs(imgfolder)
    
    
    while queue.empty() == False:
        url, level = queue.get()
        
        browser.get(url)
        responseread = browser.page_source
        #response = browser.open(url)
        #responseread = response.read()

        txtFile = txtfolder + GetHtmlFileNameFromURL(url)
        print url
        print txtFile
        #print responseread        
        
        SaveHtml(responseread, txtFile)
        
        soup = BeautifulSoup(responseread)
    
        for link in soup.findAll('a', href=True):
            href = link['href']
            if href.startswith('http') and href not in links:
                nLink = nLink + 1
                links[href] = nLink
                if level <= 1: # only crawl when level < = 1
                    queue.put( (href, level+1) )
    
        for link in links:
            print link

        for img in soup.findAll("img", src=True):
            imgsrc = img['src']
            if imgsrc not in imgUrls:
                nImg = nImg + 1
                imgUrls[imgsrc] = nImg
                imgFile = imgfolder + GetImgFileNameFromURL(imgsrc)
                downloadStatus = False
                downloadAttempts = 0
                
                while((downloadAttempts < 3) and (downloadStatus == False)):
                    downloadStatus = GetImageFromURL(imgsrc, imgFile)
                    downloadAttempts = downloadAttempts + 1
                    print downloadAttempts
        print imgUrls
            

if __name__ == "__main__":
    seedUrl = 'http://www.cs.sdu.edu.cn/getNewsDetail.do?newsId=9218'
    localDir = './'
    searchLink(seedUrl, localDir)