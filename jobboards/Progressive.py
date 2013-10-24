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

        MainPubDate = xmldoc.getElementsByTagName('lastBuildDate')[0].firstChild.data
        MainPubDate = MainPubDate[:MainPubDate.rindex(' ')]
        epochPubDate = datetime.datetime.strptime(MainPubDate, "%a, %d %b %Y %H:%M:%S").strftime('%s')

        if (epochPubDate <= self.lastFetchDate):
            return 0

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0] + "index.html"
            pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data
            pubDate = pubDate[:pubDate.rindex(' ')]

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
            offer.date_pub = datetime.datetime.strptime(pubDate, "%a, %d %b %Y %H:%M:%S").strftime('%s')
            offer.content = elt.getElementsByTagName('description')[0].firstChild.data
            offer.content = offer.content.encode( 'iso-8859-1' )

            offer.company = 'Progressive Recruitment'

            offer.location = 'NA'
            offer.cleanLocation()

            offer.contract = 'NA'
            offer.cleanContract()

            offer.salary = 'NA'
            offer.cleanSalary()

            offer.experience = 'NA'
            offer.add_db() 


    def fetch(self):
        print "Fetching " + self.name

        feed_list = ['http://www.progressiverecruitment.com/fr/job-search?task=searchAdverts&form-keywords=*&form-job-type=2&form-sector=0&form-country=69&form-jobs-salary=0&form-order-field=&form-order-dir=DESC&redirect=0&format=feed&type=rss'] # ...Système, réseaux, donnée

        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)

        for url in feed_list :
            self.fetch_url(url)


    def setup(self):
        print "setup " + self.name

class ProgressiveOffer(Offer):

    src     = 'PROGRESSIVE'
    license = ''

