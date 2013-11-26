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
        self.generateDownloadedFile()

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

    def header(self, fhandle, rpath="..", showNav=True):
        fhandle.write('<!doctype html>\n')
        fhandle.write('<html dir="ltr" lang="en">\n')
        fhandle.write('<head>\n')
        fhandle.write('\t<meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n')
        fhandle.write('\t<meta name="generator" content="JobCatcher; github.com/yoannsculo/JobCatcher" />\n')
        fhandle.write('\t<link rel="stylesheet" href="%s/css/bootstrap.min.css" />\n' % rpath)

        if showNav:
            if self.configs.globals['report']['dynamic']:
                fhandle.write('\t<link rel="stylesheet" href="%s/css/jquery-ui-1.10.3.custom.min.css" />\n' % rpath)
                fhandle.write('\t<link rel="stylesheet" href="%s/css/simplePagination.css" />\n' % rpath)
                fhandle.write('\t<link rel="stylesheet" href="%s/css/bootstrap-select.min.css" />\n' % rpath)
                fhandle.write('\t<link rel="stylesheet" href="%s/css/dynamic.css" />\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/jquery-2.0.3.min.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/bootstrap.min.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/jquery-ui-1.10.3.custom.min.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/jquery.tablesorter.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/jquery.simplePagination.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/persist-min.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/class.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript" src="%s/js/bootstrap-select.min.js"></script>\n' % rpath)
                fhandle.write('\t<script type="text/javascript">var offers_per_page = %s;</script>\n' %self.configs.globals['report']['offer_per_page'])
                fhandle.write('\t<script type="text/javascript" src="%s/js/dynamic.js"></script>\n' % rpath)
            else:
                fhandle.write('\t<link rel="stylesheet" href="%s/css/static.css" />\n' % rpath)
        fhandle.write('</head>\n')

    def navbar(self, fhandle, pagename, offers_count=None, filtered_count=None):
        offers_text = "All offers" if offers_count is None else\
            ("All %s offers" % offers_count)
        filtered_text = "Filtered offers" if filtered_count is None else\
            ("%s filtered offers" % filtered_count)
        filtered_ratio_text = "" if\
            (offers_count is None or filtered_count is None) else\
            "%s blacklisted offers (%.0f%%)" % (\
                offers_count - filtered_count,\
                100*(float) (offers_count - filtered_count) / offers_count\
            )
        fhandle.write('\t<nav class="navbar navbar-default" role="navigation">\n')
        fhandle.write('\t\t<div class="collapse navbar-collapse">\n')
        fhandle.write('\t\t\t<ul class="nav navbar-nav nav-pills">\n')
        fhandle.write('\t\t\t\t<li><a id="button-github" title="%s" href="%s"></a></li>\n'\
            % ("Check us on Github!", "https://github.com/yoannsculo/JobCatcher"))
        fhandle.write('\t\t\t\t<li class="%s"><a href="report_full.html">%s</a></li>\n'\
            % (("active" if "full" == pagename else ""), offers_text))
        fhandle.write('\t\t\t\t<li class="%s"><a href="report_filtered.html">%s</a></li>\n'\
            % (("active" if "filtered" == pagename else ""), filtered_text))
        fhandle.write('\t\t\t\t<li><p class="navbar-text">%s</p></li>\n'\
            % filtered_ratio_text)
        fhandle.write('\t\t\t</ul>\n')
        fhandle.write('\t\t</div>\n')
        fhandle.write('\t</nav>\n')

    def generateDownloadedFile(self):
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


    # def generateStatistics(self):
    #     html_dir = self.wwwdir

    #     conn = lite.connect(self.configs.globals['database'])
    #     cursor = conn.cursor()

    #     stat = open(os.path.join(html_dir, 'statistics.html'), 'w')

    #     stat.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    #     stat.write('<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">\n')
    #     stat.write("<head>\n")
    #     stat.write("<link href=\"./../css/bootstrap.css\" rel=\"stylesheet\" />\n")
    #     stat.write("<style>table{font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>\n")
    #     stat.write("<meta http-equiv=\"Content-type\" content=\"text/html; charset=utf-8\"></head>\n")
    #     stat.write("<body>\n")
    #     stat.write('\t<ul class="nav nav-pills nav-justified">\n')
    #     stat.write('\t\t<li><a href="report_full.html">All offers</a></li>\n')
    #     stat.write('\t\t<li><a href="report_filtered.html">Filtered offers</a></li>\n')
    #     stat.write('\t\t<li class="active"><a href="statistics.html">Statistics</a></li>\n')
    #     stat.write('\t</ul>\n')
    #     stat.write("<table class=\"table table-condensed\">")
    #     stat.write("<thead>")
    #     stat.write("<tr>")
    #     stat.write("<th>JobBoard</th>")
    #     stat.write("<th>Total Offers</th>")
    #     stat.write("<th>Offers not from blacklist</th>")
    #     stat.write("<th>Offers from blacklist</th>")
    #     stat.write("</tr>")
    #     stat.write("</thead>")

    #     jobboardlist = self.configs.getJobboardList()
    #     for jobboardname in jobboardlist:
    #         plugin = utilities.loadJobBoard(jobboardname, self.configs)
    #         data = plugin.fetchAllOffersFromDB()
    #         stat.write("<tr>")
    #         stat.write("<td>%s</td>" % plugin.name)
    #         stat.write("<td>%s</td>" % len(data))
    #         stat.write("<td></td>")
    #         stat.write("<td></td>")
    #         stat.write("</tr>")

    #     stat.write("</table>")
    #     stat.write("</html>")
    #     stat.close()

    def generateIndex(self, users):
        html_dir = self.wwwdir
        report = open(os.path.join(html_dir, 'index.html'), 'w')

        if not users:
            users = self.configs.getUsers()

        # report.write('<!DOCTYPE html>')
        # report.write('<html lang="en">')
        # report.write('<head>')
        # report.write('<meta charset="utf-8" />')
        # report.write('<meta http-equiv="X-UA-Compatible" content="IE=edge" />')
        # report.write('<meta name="viewport" content="width=device-width, initial-scale=1.0" />')
        # report.write('<meta name="description" content="" />')
        # report.write('<meta name="author" content="" />')
        # report.write('<link rel="shortcut icon" href="../../docs-assets/ico/favicon.png" />')

        # report.write('<title>Family jobcatcher</title>')

        # report.write('<!-- Bootstrap core CSS -->')
        # report.write('<link href="css/bootstrap.css" rel="stylesheet" />')

        # report.write('<!-- Custom styles for this template -->')
        # report.write('<link href="jumbotron-narrow.css" rel="stylesheet" />')

        # report.write('<!-- Just for debugging purposes. Don\'t actually copy this line! -->')
        # report.write('<!--[if lt IE 9]><script src="../../docs-assets/js/ie8-responsive-file-warning.js"></script><![endif]-->')

        # report.write('<!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->')
        # report.write('<!--[if lt IE 9]>')
        # report.write('<script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>')
        # report.write('<script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>')
        # report.write('<![endif]-->')
        # report.write('</head>')

        self.header(report, '.', False)

        report.write('<body>\n')
        report.write('<div class="container">\n')
        report.write('<div class="header">\n')
        report.write('<ul class="nav nav-pills pull-right">\n')
        report.write('<li class="active"><a href="#">Home</a></li>\n')
        report.write('<li><a href="#">About</a></li>\n')
        report.write('<li><a href="#">Contact</a></li>\n')
        report.write('</ul>\n')
        report.write('<h3 class="text-muted">Family jobcatcher</h3>\n')
        report.write('</div>\n')

        report.write('<div class="jumbotron">\n')
        report.write('<h1>Jobcatcher Community</h1>\n')
        report.write('<p class="lead">Find the job in colaborative mode</p>\n')
        report.write('<p>\n')

        for user in users:
            report.write('<a class="btn btn-lg btn-success" href="./%s/report_full.html" role="button">%s</a>' % (user, user))

        report.write('</p>\n')
        report.write('</div>\n')
        report.write('<div class="footer">\n')
        report.write('<p>&copy; JobCatcher</p>\n')
        report.write('</div>\n')
        
        report.write('</div> <!-- /container -->\n')

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
                report = open(os.path.join(html_dir, 'report_filtered.html'), 'w')
                data = data_filtered
            else:
                report = open(os.path.join(html_dir, 'report_full.html'), 'w')
                data = data_full

            self.header(report)

            report.write('<body>\n')
            # page header def navbar(self, fhandle, pagename, offers_count=None, filtered_count=None):
            pagename = "filtered" if filtered else "full"
            self.navbar(report, pagename, count_full, count_filtered)

            # page body
            report.write('\t<table id="offers" class="table table-condensed">\n')
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
                    row[13], row[14], row[15], row[16], row[17], row[18]
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
                report.write('\t\t\t\t<td class="salary">' + offer.salary + '</td>\n')

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
            report.write('\t</table>\n')

            # Last generated
            lastupdate = datetime.datetime.fromtimestamp(int(time.time()))
            report.write('<div class="footer">\n')
            report.write('<p>&copy; JobCatcher / last generated %s</p>\n' % lastupdate)
            report.write('</div>\n')

            report.write('</body>\n')
            report.write('</html>\n')
            report.close()
