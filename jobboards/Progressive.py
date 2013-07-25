#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Guillaume DAVID'
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import re
import time
import codecs

from jobcatcher import JobCatcher
from jobcatcher import Jobboard
from jobcatcher import Offer
from jobcatcher import Location

from xml.dom import minidom
import datetime
import utilities

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

class Progressive(Jobboard):

    def __init__(self):
        self.name = "PROGRESSIVE"
        self.url = "http://fr.progressiverecruitment.com"
        self.lastFetch = ""
        self.processingDir = self.dlDir + "/progressive"
        self.lastFetchDate = 0

    def fetch_url(self, url):
        filename = url.split('/')[-1]
        utilities.download_file(url, self.processingDir)

        xmlfile = os.path.join(self.processingDir, filename)
        fileObj = codecs.open( xmlfile, "r", "utf-8" )
        content = fileObj.read()
        xmldoc = minidom.parseString( content )
        fileObj.close()
        #xmldoc = minidom.parse(xmlfile)

        MainPubDate = xmldoc.getElementsByTagName('posted')[0].firstChild.data
        epochPubDate = datetime.datetime.strptime(MainPubDate, "%d/%m/%Y %H:%M:%S").strftime('%s')

        if (epochPubDate <= self.lastFetchDate):
            return 0

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0] + "index.html"
            pubDate = elt.getElementsByTagName('posted')[0].firstChild.data

            if (epochPubDate <= self.lastFetchDate):
                break

#            if (not os.path.isfile(os.path.join(self.processingDir, link.split('/')[-1]))):
            offer = ProgressiveOffer()
            guid = elt.getElementsByTagName('guid')[0].firstChild.data
            offer.ref = guid.split('/')[-2]
            print "Processing %s" % (offer.ref)
            offer.date_add = int(time.time())
            loc = Location()
            offer.lat = loc.lat
            offer.lon = loc.lon
            offer.title = title.encode( 'iso-8859-1' )
            offer.url = link
            offer.date_pub = datetime.datetime.strptime(pubDate, "%d/%m/%Y %H:%M:%S").strftime('%s')
            offer.content = elt.getElementsByTagName('description')[0].firstChild.data
            offer.content = offer.content.encode( 'iso-8859-1' )
            offer.company = 'Progressive Recruitment'
            offer.location = elt.getElementsByTagName('location')[0].firstChild.data
            offer.location = offer.location.encode( 'iso-8859-1' )
            offer.location = re.sub(ur'IDF', "Île-de-France", offer.location)
            offer.contract = elt.getElementsByTagName('job_type')[0].firstChild.data
            offer.contract = re.sub(ur' Perm ','CDI', offer.contract)
            offer.salary = elt.getElementsByTagName('salary')[0].firstChild.data
            offer.salary = offer.salary.encode( 'iso-8859-1' )
            offer.cleanSalary()
            offer.experience = 'experimenté'
            offer.add_db() 


    def fetch(self):
        print "Fetching " + self.name

        feed_list = ['http://fr.progressiverecruitment.com/fr/JobSearch/Rss/France/CDI/69/2/0/0/0/1/index.html'] # ...Système, réseaux, donnée

        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)

        for url in feed_list :
            self.fetch_url(url)


    def setup(self):
        print "setup " + self.name

class ProgressiveOffer(Offer):

    src     = 'PROGRESSIVE'
    license = ''

    def cleanSalary(self):
        self.salary = utilities.filter_salary_fr(self.salary)
        return
