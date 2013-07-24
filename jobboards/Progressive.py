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

from utilities import *

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
        download_file(url, self.processingDir)

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
        # TODO : use regexp once whe have a better view of possible combinations
        self.salary = re.sub(ur'Selon diplôme et expérience', "NA", self.salary)
        self.salary = re.sub(ur'fixe + variable selon profil', "NA", self.salary)
        self.salary = re.sub(ur'A définir selon profil', "NA", self.salary)
        self.salary = re.sub(ur'A DEFINIR SELON PROFIL', "NA", self.salary)
        self.salary = re.sub(ur'à défninir selon profil', "NA", self.salary)
        self.salary = re.sub(ur'à définir selon profils', "NA", self.salary)
        self.salary = re.sub(ur'à définir selon expérience', "NA", self.salary)
        self.salary = re.sub(ur'A négocier selon profil', "NA", self.salary)
        self.salary = re.sub(ur'A NEGOCIER SELON PROFIL', "NA", self.salary)
        self.salary = re.sub(ur'à négocier selon profil', "NA", self.salary)
        self.salary = re.sub(ur'A négocier selon expérience', "NA", self.salary)
        self.salary = re.sub(ur'A voir selon profil', "NA", self.salary)
        self.salary = re.sub(ur'En fonction du profil', "NA", self.salary)
        self.salary = re.sub(ur'Selon profil et expériences', "NA", self.salary)
        self.salary = re.sub(ur'Selon profil et expérience', "NA", self.salary)
        self.salary = re.sub(ur'selon profil et expérience +', "NA", self.salary)
        self.salary = re.sub(ur'selon profil et expérience', "NA", self.salary)
        self.salary = re.sub(ur'selon profil et exp', "NA", self.salary)
        self.salary = re.sub(ur'selon profil et avantages', "NA", self.salary)
        self.salary = re.sub(ur'selon votre profil', "NA", self.salary)
        self.salary = re.sub(ur'Selon votre profil', "NA", self.salary)
        self.salary = re.sub(ur'selon le profil', "NA", self.salary)
        self.salary = re.sub(ur'Selon le profil', "NA", self.salary)
        self.salary = re.sub(ur'Selon profils', "NA", self.salary)
        self.salary = re.sub(ur'Selon profil', "NA", self.salary)
        self.salary = re.sub(ur'selon profil', "NA", self.salary)
        self.salary = re.sub(ur'selon Profil', "NA", self.salary)
        self.salary = re.sub(ur'Selon Profil', "NA", self.salary)
        self.salary = re.sub(ur'SELON PROFIL', "NA", self.salary)
        self.salary = re.sub(ur'selo profil', "NA", self.salary)
        self.salary = re.sub(ur'selon l\'expérience', "NA", self.salary)
        self.salary = re.sub(ur'selon experience', "NA", self.salary)
        self.salary = re.sub(ur'selon expérience', "NA", self.salary)
        self.salary = re.sub(ur'Selon expérience', "NA", self.salary)
        self.salary = re.sub(ur'Selon expérince', "NA", self.salary)
        self.salary = re.sub(ur'Selon Expérience', "NA", self.salary)
        self.salary = re.sub(ur'Selon experience', "NA", self.salary)
        self.salary = re.sub(ur'SELON EXPERIENCE', "NA", self.salary)
        self.salary = re.sub(ur'Selon compétences', "NA", self.salary)
        self.salary = re.sub(ur'Selon compétence', "NA", self.salary)
        self.salary = re.sub(ur'selon exp.', "NA", self.salary)
        self.salary = re.sub(ur'suivant profil', "NA", self.salary)
        self.salary = re.sub(ur'grille fonction publique', "NA", self.salary)
        self.salary = re.sub(ur'à déterminer', "NA", self.salary)
        self.salary = re.sub(ur'à convenir', "NA", self.salary)
        self.salary = re.sub(ur'à négocier', "NA", self.salary)
        self.salary = re.sub(ur'a négocier', "NA", self.salary)
        self.salary = re.sub(ur'a negocier', "NA", self.salary)
        self.salary = re.sub(ur'à negocier', "NA", self.salary)
        self.salary = re.sub(ur'A négocier', "NA", self.salary)
        self.salary = re.sub(ur'A NEGOCIER', "NA", self.salary)
        self.salary = re.sub(ur'A negocier', "NA", self.salary)
        self.salary = re.sub(ur'à définir', "NA", self.salary)
        self.salary = re.sub(ur'À définir', "NA", self.salary)
        self.salary = re.sub(ur'A définir', "NA", self.salary)
        self.salary = re.sub(ur'A DEFINIR', "NA", self.salary)
        self.salary = re.sub(ur'A definir', "NA", self.salary)
        self.salary = re.sub(ur'A défnir', "NA", self.salary)
        self.salary = re.sub(ur'A discuter', "NA", self.salary)
        self.salary = re.sub(ur'en fonction exp.', "NA", self.salary)
        self.salary = re.sub(ur'en fonction du profil', "NA", self.salary)
        self.salary = re.sub(ur'Négociable', "NA", self.salary)
        self.salary = re.sub(ur'négociable', "NA", self.salary)
        self.salary = re.sub(ur'negociable', "NA", self.salary)
        self.salary = re.sub(ur'NEGOCIABLE', "NA", self.salary)
        self.salary = re.sub(ur'Negotiable', "NA", self.salary)
        self.salary = re.sub(ur'non indiqué', "NA", self.salary)
        self.salary = re.sub(ur'non communiqué', "NA", self.salary)
        self.salary = re.sub(ur'NON COMMUNIQUE', "NA", self.salary)
        self.salary = re.sub(ur'non précisé', "NA", self.salary)
        self.salary = re.sub(ur'Non précisé', "NA", self.salary)
        self.salary = re.sub(ur'Voir annonce', "NA", self.salary)
        self.salary = re.sub(ur'GRILLE DE LA FPT', "NA", self.salary)
        self.salary = re.sub(ur'Grille', "NA", self.salary)
        self.salary = re.sub(ur'confidentiel', "NA", self.salary)
        self.salary = re.sub(ur'TBD', "NA", self.salary)
        self.salary = re.sub(ur'N.S.', "NA", self.salary)
        self.salary = re.sub(ur'ANNUEL', "NA", self.salary)
        self.salary = re.sub(ur'NC K€ brut/an', "NA", self.salary)
        self.salary = re.sub(ur'xx K€ brut/an', "NA", self.salary)
              # self.salary = re.sub(ur'0K€ brut/an', "NA", self.salary)
        self.salary = re.sub(ur'-K€ brut/an', "NA", self.salary)

        return 0
