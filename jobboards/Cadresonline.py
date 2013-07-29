#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Jonathan Courtoux <j.courtoux@gmail.com>'
__copyright__ = 'Copyright (C) 2013 jonathan courtoux'
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import re
import time

from jobcatcher import JobCatcher
from jobcatcher import Jobboard
from jobcatcher import Offer
from jobcatcher import Location

from xml.dom import minidom
import datetime
import utilities

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

class Cadresonline(Jobboard):

    def __init__(self):
        self.name = "Cadresonline"
        self.url = "http://www.cadresonline.com"
        self.lastFetch = ""
        self.processingDir = self.dlDir + "/cadresonline"
        self.lastFetchDate = 0

    def fetch_url(self, url):
        filename = url.split('/')[-1]
        utilities.download_file(url, self.processingDir)

        xmldoc = minidom.parse(os.path.join(self.processingDir, filename))

        MainPubDate = xmldoc.getElementsByTagName('pubDate')[0].firstChild.data

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0]
            pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data

        if (not os.path.isfile(os.path.join(self.processingDir, link.split('/')[-1]))):
                print "Downloading %s" % (link)
                utilities.download_file(link, self.processingDir)

    def fetch(self):
        print "Fetching " + self.name

        feed_list = ['http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615'] # Développeur
        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)

        for url in feed_list :
            self.fetch_url(url)

        self.processOffers()

    def processOffers(self):
        for file in os.listdir(self.processingDir):
            if (not file.lower().endswith('.html')):
                    continue

            print "Processing %s" % (file)
            offer = CadreonlineOffer()
            res = offer.loadFromHtml(os.path.join(self.processingDir, file))
            if (res != 0):
                continue
            offer.date_add = int(time.time())
            loc = Location()
            # loc.loadFromAddress(offer.location)
            offer.lat = loc.lat
            offer.lon = loc.lon
            if (offer.add_db() == 0):
                os.remove(os.path.join(self.processingDir,file))

    def setup(self):
        print "setup " + self.name

class CadreonlineOffer(Offer):

    src     = 'CADRESONLINE'
    license = ''

    def loadFromHtml(self, filename):
        fd = open(filename, 'rb')
        html = fd.read()
        fd.close()

        soup = BeautifulSoup(html, fromEncoding="UTF-8")

        # Offer still available ?
        res = soup.body.find('div', attrs={'class':'boxSingleMain box'})
        if (res != None):
            content = res.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton c\
                i-dessous pour revenir à l\'onglet Mes Offres'):
                return 1

        # Title
        res = soup.body.find('div', attrs={'class':'boxMain boxOffres box'})
        if (res == None):
            return -1
        res = res.find("h2", attrs={'class':'borderBottom0'})
        self.title = HTMLParser().unescape(res.text)
        matchObj = re.match( ur'Offre d\'emploi (.*)', self.title)
        if matchObj:
            self.title = matchObj.group(1)

        # Other information
        res = soup.body.find('div', attrs={'class':'content1_9ImbLeft'})
        res = res.findAll("tr")

        for elt in res:
            th = elt.find('th')
            td = elt.find('td')

            if (th.text == u'Salaire :'):
                self.cleanSalary()

            if (th.text == u'Expérience :'):
                self.experience = HTMLParser().unescape(td.text)

        # Content
        res = soup.body.find('div', attrs={'class':'contentWithDashedBorderTop marginTop boxContent'})
        res = res.find('div', attrs={'class':'boxContentInside'})
        self.content = HTMLParser().unescape(res.text);

        self.url = "http://cadresonline.fr/" + os.path.basename(filename)

        return 0
