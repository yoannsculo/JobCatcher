#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
    'Yankel Scialom <yankel.scialom@mail.com>'
]
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

# System
import os
import re
import time
import datetime

# Third party
import sqlite3 as lite

# Jobcatcher
import utilities
from jc.data import Offer

class ReportGenerator(object):
    """Generic Class forcreate new jobboard"""
    def __init__(self, configs=None):
        self._rootdir = configs.globals['rootdir']
        self._wwwdir = configs.globals['wwwdir']
        self._configs = configs

    @property
    def wwwdir(self):
        return self._wwwdir

    @wwwdir.setter  
    def wwwdir(self, value):
        self._wwwdir = value

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value

    def generate(self, selecteduser):
        self.generateReport(selecteduser, True)
        self.generateReport(selecteduser, False)
        # self.generateStatistics()
        self.generateIndex(selecteduser)
        self.generateP2PIndex()

    def _getSQLFilterFeedid(self, feedidslist):
        sql = "feedid in ("
        for idx in range(len(feedidslist)):
            sql += "'%s'" % feedidslist[idx]
            if idx != len(feedidslist) - 1:
                sql += ', '

        sql += ")"

        return sql

    def box(self, style, text):
        if style == "":
            style = "default"

        css = " label-%s" % style
        return '<span class="label%s">%s</span>' % (css, text)

    def csstag(self, rpath, filename):
        return '\t<link rel="stylesheet" href="%s/css/%s" />\n' % (rpath, filename)

    def jstag(self, rpath, filename):
        return '\t<script type="text/javascript" src="%s/js/%s"></script>\n' % (rpath, filename)

    def header(self, fhandle, title, rpath="..", showNav=True, extra=""):
        fhandle.write('<!doctype html>\n')
        fhandle.write('<html dir="ltr" lang="en">\n')
        fhandle.write('<head>\n')
        fhandle.write('\t<meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n')
        fhandle.write('\t<meta name="generator" content="JobCatcher; github.com/yoannsculo/JobCatcher" />\n')
        fhandle.write(self.csstag(rpath, "bootstrap.min.css"))

        if showNav:
            if self.configs.globals['report']['dynamic']:
                # css
                for cssfile in [\
                    "jquery-ui-1.10.3.custom.min.css",\
                    "bootstrap-select.min.css",\
                    "daterangepicker-bs3.css",\
                    "dynamic.css"\
                ]:
                    fhandle.write(self.csstag(rpath, cssfile))
                # js
                fhandle.write('\t<script type="text/javascript">var offers_per_page = %s;</script>\n'\
                    % self.configs.globals['report']['offer_per_page'])
                for jsfile in [\
                    "jquery-2.0.3.min.js",\
                    "bootstrap.min.js",\
                    "jquery-ui-1.10.3.custom.min.js",\
                    "persist-min.js",\
                    "class.js",\
                    "bootstrap-select.min.js",\
                    "moment.min.js",\
                    "daterangepicker.js",\
                    "dynamic.js",\
                ]:
                    fhandle.write(self.jstag(rpath, jsfile))
            else:
                fhandle.write('\t<link rel="stylesheet" href="%s/css/static.css" />\n' % rpath)
        fhandle.write(extra)
        fhandle.write('\t<title>Jobcatcher &mdash; %s</title>\n' % title)
        fhandle.write('</head>\n')

    def navbar(self, fhandle, pagename, offers_count=None, filtered_count=None):
        offers_text = "All offers" if offers_count is None else\
            ("All %s offers" % offers_count)
        filtered_text = "Filtered offers" if filtered_count is None else\
            ("%s filtered offers" % filtered_count)
        try:
            filtered_ratio_text = "" if\
            (offers_count is None or filtered_count is None) else\
            "%s blacklisted offers (%.0f%%)" % (\
                offers_count - filtered_count,\
                100*(float) (offers_count - filtered_count) / offers_count\
            )
        except:
            filtered_ratio_text = "?"

        fhandle.write('\t<nav class="navbar navbar-fixed-top" role="navigation">\n')
        fhandle.write('\t\t<div class="collapse navbar-collapse">\n')
        fhandle.write('\t\t\t<ul class="nav navbar-nav nav-pills">\n')
        fhandle.write('\t\t\t\t<li><a title="Back to the community page" href="../index.html">%s</a></li>\n'\
            % '<span class="glyphicon glyphicon-circle-arrow-left"></span> Community')
        fhandle.write('\t\t\t\t<li class="%s"><a href="report_full.html">%s</a></li>\n'\
            % (("active" if "full" == pagename else ""), offers_text))
        fhandle.write('\t\t\t\t<li class="%s"><a href="report_filtered.html">%s</a></li>\n'\
            % (("active" if "filtered" == pagename else ""), filtered_text))
        fhandle.write('\t\t\t\t<li><p class="navbar-text">%s</p></li>\n'\
            % filtered_ratio_text)
        fhandle.write('\t\t\t</ul>\n')
        fhandle.write('\t\t</div>\n')
        fhandle.write('\t</nav>\n')

    def footer(self, fhandle):
        lastupdate = datetime.datetime.fromtimestamp(int(time.time()))
        fhandle.write('\t<footer>&copy; JobCatcher %s\n'\
            % '<a class="icon-github" title="Check us on Github!"'\
            + 'href="https://github.com/yoannsculo/JobCatcher"></a>'\
        )
        fhandle.write('\t\t&mdash; generated %s\n' % lastupdate)
        fhandle.write('\t</footer>\n')

    def generateP2PIndex(self):
        # Search feeds
        feeds = utilities.findFiles(self.rootdir, '*.feed')
        fl = open(os.path.join(self.wwwdir, 'feeds.txt'), 'w')
        for f in feeds:
            fl.write(os.path.basename("%s\n" % f))
        fl.close()

        # Search pages
        dirs = os.listdir(self.rootdir)
        for d in dirs:
            pagedir = '%s/%s' % (self.rootdir, d)
            pages = utilities.findFiles(pagedir, '*.page')
            saveto = os.path.join('%s/%s.txt' % (self.wwwdir, d))
            pl = open(saveto, 'w')
            for p in pages:
                filename = re.sub(r'.*?/pages/', '', p)
                pl.write("%s\n" % filename)
            pl.close()

    def generateIndex(self, users):
        html_dir = self.wwwdir
        report = open(os.path.join(html_dir, 'index.html'), 'w')

        if not users:
            users = self.configs.getUsers()

        # HTML header
        footerstyle='\t<link rel="stylesheet" href="./css/index.css" />\n'
        self.header(report, 'community', '.', False, footerstyle)
        # HTML body
        report.write('<body>\n')
        # special CSS
        report.write('\t<div class="container">\n')
        # navigation bar
        report.write('\t\t<nav role="nav">\n')
        report.write('\t\t\t<ul class="nav nav-pills pull-right">\n')
        report.write('\t\t\t\t<li class="active disabled"><a href="#">Home</a></li>\n')
        report.write('\t\t\t\t<li class="disabled"><a href="#" title="Comming soon">About</a></li>\n')
        report.write('\t\t\t\t<li class="disabled"><a href="#" title="Comming soon">Contact</a></li>\n')
        report.write('\t\t\t</ul>\n')
        report.write('\t\t\t<h3 class="text-muted">Family jobcatcher</h3>\n')
        report.write('\t\t</nav>\n\n')
        # central frame
        report.write('\t\t<div class="jumbotron">\n')
        report.write('\t\t\t<h1>Jobcatcher Community</h1>\n')
        report.write('\t\t\t<p class="lead">Find the job in colaborative mode</p>\n')
        # users
        report.write('\t\t\t<p>\n')
        for user in users:
            report.write('\t\t\t\t<a class="btn btn-lg btn-info" href="./%s/report_full.html" role="button">%s</a>\n' % (user, user))
        report.write('\t\t\t</p>\n')
        # end central frame
        report.write('\t\t</div><!-- .jumbotron -->\n')
        # end main container
        report.write('\t</div><!-- .container -->\n')
        # footer
        self.footer(report)

        report.write('</body>\n')
        report.write('</html>\n')
        report.close()

    def generateReport(self, users, filtered=True):
        if not users:
            users = self.configs.getUsers()

        feedsinfo = self.configs.getFeedsInfo(users)

        for user in users:
            feedidslist = self.configs.getFeedIdsForUser(user)
            # Directory
            html_dir = "%s/%s" % (self.wwwdir, user)
            if not os.path.exists(html_dir):
                os.makedirs(html_dir)

            # Query
            conn = lite.connect(self.configs.globals['database'])
            cursor = conn.cursor()
            data = None

            feedidfilter = self._getSQLFilterFeedid(feedidslist)
            sql_filtered = "SELECT * FROM offers WHERE %s and company not IN (SELECT company FROM blacklist) ORDER BY date_pub DESC" % feedidfilter
            sql_full = "SELECT * FROM offers where %s ORDER BY date_pub DESC" % feedidfilter
            cursor.execute(sql_filtered)
            data_filtered = cursor.fetchall()
            cursor.execute(sql_full)
            data_full = cursor.fetchall()
            count_filtered = len(data_filtered)
            count_full = len(data_full)
            if (filtered):
                title = 'filtered job offers'
                report = open(os.path.join(html_dir, 'report_filtered.html'), 'w')
                data = data_filtered
            else:
                title = 'job offers'
                report = open(os.path.join(html_dir, 'report_full.html'), 'w')
                data = data_full

            self.header(report, title)

            report.write('<body>\n')
            # page header def navbar(self, fhandle, pagename, offers_count=None, filtered_count=None):
            pagename = "filtered" if filtered else "full"
            self.navbar(report, pagename, count_full, count_filtered)

            # page body
            report.write('\t<div class="main"><table id="offers" class="table table-condensed">\n')
            # table header
            report.write('\t\t<thead>\n')
            report.write('\t\t\t<tr id="lineHeaders">\n')
            report.write('\t\t\t\t<th class="pubdate">Pubdate</th>\n')
            # report.write('\t\t\t\t<th class="type">Type</th>\n')
            report.write('\t\t\t\t<th class="title">Title</th>\n')
            report.write('\t\t\t\t<th class="company">Company</th>\n')
            report.write('\t\t\t\t<th class="location">Location</th>\n')
            report.write('\t\t\t\t<th class="contract">Contract</th>\n')
            report.write('\t\t\t\t<th class="salary">Salary</th>\n')
            report.write('\t\t\t\t<th class="source">Source</th>\n')
            report.write('\t\t\t</tr>\n')
            if self.configs.globals['report']['dynamic']:
                report.write('\t\t\t<tr id="lineFilters">\n')
                report.write('\t\t\t\t<td class="pubdate"></td>\n')
                # report.write('\t\t\t\t<td class="type"></td>\n')
                report.write('\t\t\t\t<td class="title"></td>\n')
                report.write('\t\t\t\t<td class="company"></td>\n')
                report.write('\t\t\t\t<td class="location"></td>\n')
                report.write('\t\t\t\t<td class="contract"></td>\n')
                report.write('\t\t\t\t<td class="salary"></td>\n')
                report.write('\t\t\t\t<td class="source"></td>\n')
                report.write('\t\t\t</tr>\n')
            report.write('\t\t</thead>\n')
            # table body
            report.write('\t\t<tbody>\n')

            s_date = ''
            for row in data:
                offer = Offer()
                offer.load(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], row[8], row[9], row[10], row[11], row[12],
                    row[13], row[14], row[15], row[16], row[17], row[18],
                    row[19], row[20], row[21], row[22], row[23], row[24],
                    row[25],row[26]
                )

                if (not self.configs.globals['report']['dynamic'] and s_date != offer.date_pub.strftime('%Y-%m-%d')):
                    s_date = offer.date_pub.strftime('%Y-%m-%d')
                    report.write('\t\t\t<tr class="error">\n');
                    report.write('\t\t\t\t<td colspan="8" />\n')
                    report.write('\t\t\t</tr>\n')

                report.write('\t\t\t<tr>\n')
                if offer.state == "DISABLED":
                    report.write('\t\t\t\t<td class="pubdate">%s</td>\n' % self.box('danger', offer.date_pub.strftime('%Y-%m-%d')))
                else:
                    report.write('\t\t\t\t<td class="pubdate">%s</td>\n' % offer.date_pub.strftime('%Y-%m-%d'))
                #report.write('\t\t\t\t<td class="type"><span class="label label-success">noSSII</span></td>\n')
                report.write('\t\t\t\t<td class="title"><a href="'+offer.url+'">' + offer.title + '</a></td>\n')
                report.write('\t\t\t\t<td class="company">' + offer.company + '</td>\n')
                # Location
                report.write('\t\t\t\t<td class="location">')
                if offer.department:
                    report.write("%s&nbsp;" % self.box('primary', offer.department))
                report.write(offer.location)
                report.write('</td>\n')

                # contract
                duration = ""
                report.write('\t\t\t\t<td class="contract">')
                if offer.duration:
                    duration = "&nbsp;%s" % self.box('info', "%s  mois" % offer.duration)
                if ('CDI' in offer.contract):
                    report.write(self.box('success', offer.contract))
                    report.write(duration)
                elif ('CDD' in offer.contract):
                    report.write(self.box('warning', offer.contract))
                    report.write(duration)
                else:
                    report.write(self.box('', offer.contract))
                    report.write(duration)
                report.write('</td>\n')
                if offer.salary_cleaned == 'NA' or offer.salary == offer.salary_cleaned:
                    report.write('\t\t\t\t<td class="salary">' + offer.salary_cleaned + '</td>\n')
                else:
                    report.write('\t\t\t\t<td class="salary">' + self.box('primary', offer.salary_cleaned) + '</td>\n')
                # Source
                feedurl = feedsinfo[offer.src][offer.feedid]['url']
                report.write('\t\t\t\t<td class="source"><a href="%s">%s</a></td>\n' % \
                             (
                                 re.sub('&', '&amp;', feedurl),
                                 offer.src,
                             )
                )
                report.write('\t\t\t</tr>\n')

            # closure
            report.write('\t</table></div>\n')

            # footer
            self.footer(report)

            report.write('</body>\n')
            report.write('</html>\n')
            report.close()
