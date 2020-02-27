#!/usr/bin/python3
import urllib
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
from datetime import datetime, date
import threading
import hashlib


# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class y_newsfilter:
    """Class to extract a specific stock's News from finance.yahoo.com"""

    # global accessors
    n_df0 = ""          # DataFrame - Full list of top gainers
    n_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    n_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    soup = ""           # the entire HTML doc
    ul_tag_dataset = ""      # BS4 handle of the <tr> extracted data
    inst_uid = 0
    cycle = 0           # class thread loop counter
    symbol = ""         # Unique company symbol

    def __init__(self, i, symbol, global_args):
        # WARNING: There is/can-be NO checking to ensure this is a valid/real symbol
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT inst' % cmi_debug )
        self.args = global_args
        # init empty DataFrame with present colum names
        self.n_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.n_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.n_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.inst_uid = i
        self.symbol = symbol
        return

# method #1
    def scan_news_depth_0(self):
        """Connect to finance.yahoo.com and process the raw news HTML data tables from"""
        """the complex MAIN (highlevel) news parent webpage for an individual stcok [Stock:News ]."""
        """Does not extract any news atricles, items or data fields. Just sets up the element extraction zone."""
        """Returns a BS4 onbject handle pointing to correct news section for deep element extraction."""

        cmi_debug = __name__+"::"+self.scan_news_depth_0.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        news_url = "https://finance.yahoo.com/quote/" + self.symbol + "/news?p=" + self.symbol      # form the correct URL
        logging.info('%s - URL:' % (cmi_debug) )
        print ( f"Extract news for: SDC @: {news_url}" )
        with urllib.request.urlopen(news_url) as url:
            s = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            self.soup = BeautifulSoup(s, "html.parser")
        logging.info('%s - save data object handle' % cmi_debug )
        self.ul_tag_dataset = self.soup.find(attrs={"class": "My(0) Ov(h) P(0) Wow(bw)"} )
        logging.info('%s - close main news page url handle' % cmi_debug )
        url.close()
        return

    def news_article_depth_1(self, url):
        """Analyze 1 (ONE) individual news article taken from the list of article within the MAIN news HTNML page"""
        """and setup the data extractor to point into the KEY element zone within that news HTML dataset so that"""
        """critical news elements, fields & data objects can be deeply extracted (from this 1 news article)."""
        """Note: - This has to be called for each article showing in the MAIN news page"""
        """Note: - Calling this recurisvely will be network expensive...but that is the plan"""

        cmi_debug = __name__+"::"+self.news_article_depth_1.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        deep_url = url      # pass in the url that we want to deeply analyze
        logging.info('%s - Follow URL:' % (cmi_debug) )
        logging.info('%s - read html stream' % cmi_debug )
        with urllib.request.urlopen(deep_url) as url:
            f = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            soup = BeautifulSoup(f, "html.parser")

        logging.info('%s - ' % cmi_debug )
        #
        # fnl_tag_dataset = soup.find_all('a')
        tag_dataset = soup.div.find_all(attrs={'class': 'D(tbc)'} )
        logging.info('%s - close news article url handle' % cmi_debug )
        url.close()
        return tag_dataset

    def news_article_depth_1a(self):
        """Hacking - # OPTIMIZEd extraction """
        """No sub article deep follow. Just try to get to the date from the TOP level"""

        cmi_debug = __name__+"::"+self.news_article_depth_1.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        # age_tag_dataset = self.ul_tag_dataset.find(attrs={'class': 'C(#959595)'} )
        #C(#959595) Fz(11px) D(ib) Mb(6px)

        mhl_1a = self.ul_tag_dataset.div.find_all(attrs={'class': 'C(#959595)'})
        mhl_2a = self.ul_tag_dataset.find(attrs={'class': 'C(#959595)'})
        mhl_3a = self.ul_tag_dataset.find_all(attrs={'class': 'C(#959595)'})
        jsp_1a = self.ul_tag_dataset.find_all('li')
        jsp_2a = self.ul_tag_dataset.find(attrs={'class': 'C(#959595) Fz(11px) D(ib) Mb(6px)'} )
        # for i in range(len(jsp_1a)):
        #    h = jsp_1a[i]
        #    print ( f"====== Element: #{i} ===============" )
        #    print ( f"News outlet: {h}" )
        # vtaglist = []
        # for vtag in self.ul_tag_dataset.find_all(True):   # a_subset[erow].find_all(True):
        #    vtaglist.append(vtag.name)
        # print ( f"*** HACKING-0: Unique tags: {set(vtaglist)}" )
        # age_tag_dataset = self.ul_tag_dataset.find({'class': 'Ov(h)'} )
        #print ( f"*** HACKING-1: Top level Age: {age_tag_dataset}" )
        print ( f"*** HACKING-1: Top level: {mhl_1a}" )
        for s in mhl_1a.next_elements:
            print ( f"*** HACKING-2: level 0: {s}" )
        print ( f"*** HACKING-1: level 1: {mhl_2a.next_sibling}" )
        #print ( f"*** HACKING-1: Top level Age: {mhl_2a.next_element}" )
        #print ( f"*** HACKING-1: Top level Age: {mhl_2a.next_element}" )
        return

# method #2
    def read_allnews_depth_0(self):
        """Cycle though the MAIN top-level NEWS page and prepare a nice list of ALL of the articles."""
        """For each article, extract some KEY high-level news elements (i.e. Headline, Brief, URL to real article."""
        """NOTE: This is main controller logic loop because we're at the TOP high-level news page for this stock."""
        """Wrangle, clean/convert/format the data correctly"""

        cmi_debug = __name__+"::"+self.read_allnews_depth_0.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        self.n_df0.drop(self.n_df0.index, inplace=True)
        x = 0    # row counter Also leveraged for unique dataframe key

        # element zones from main dataset @ depth_0
        li_superclass = self.ul_tag_dataset.find_all(attrs={"class": "js-stream-content Pos(r)"} )
        li_subset = self.ul_tag_dataset.find_all('li')
        mini_headline = self.ul_tag_dataset.div.find_all(attrs={'class': 'C(#959595)'})
        #micro_headline = self.soup.find_all("i") #attrs={'class': 'Mx(4px)'})

        r_url = l_url = 0
        for datarow in range(len(li_subset)):
            html_element = li_subset[datarow]
            x += 1
            print ( f"====== News item: #{x} ===============" )
            print ( f"News outlet: {html_element.div.find(attrs={'class': 'C(#959595)'}).string }" )
            #print ( f"News outlet2: {datarow[0].contents}" )

            # FRUSTRATING element that cant be locally extracted from High-level page
            # TODO: Figure out WHY?
            # extracting this from the main page would increase speed by 10x
            # print ( f"DOT: {html_element.i.find(attrs={'class': 'Mx(4px)'}) }" )"""

            # Identify Local or Remote news article
            # An href that begins with http:// is a hard link to external news outlet that forces us off-site
            # Otherwise we'll see a raw Rescource Path /..../..../
            rhl_url = False     # safety pre-set
            url_p = urlparse(html_element.a.get('href'))
            if url_p.scheme == "https" or url_p.scheme == "http":    # check URL scheme specifier
                print ( f"Remote news URL: {url_p.netloc}  - Artcile path: {url_p.path}" )
                #  ParseResult(scheme='https', netloc='techcrunch.com', path='/2020/02/10/what-happened-to-slack-today/', params='', query='', fragment=''
                rhl_url = True    # This URL is remote
                r_url += 1        # count remote URLs
            else:
                print ( f"Local news URL:  finance.yahoo.com  - Article path: {html_element.a.get('href')}" )
                l_url += 1        # count local URLs

            print ( f"News headline: {html_element.a.text}" )
            print ( "News Short Brief: {:.400}".format(html_element.p.text) )    # truncate long New Brief headlines to max 400 chars

            # generate a unuque hash for each new URL, for easier dupe tests & comparrisons etc
            url_prehash = html_element.a.get('href')
            result = hashlib.sha256(url_prehash.encode())
            print ( f"Hash encoded URL: {result.hexdigest()}" )

            # BIG logic decision here...!!!
            if self.args['bool_deep'] is True:        # go DEEP & process each news article deeply?
                if rhl_url == False:                  # yahoo,com local? or remote hosted non-yahoo.com article?
                    a_deep_link = 'https://finance.yahoo.com' + url_prehash
                    self.extract_article_data(a_deep_link)      # deeply extract data from this 1 news article
                    logging.info('%s - Extracting NEWS from 1 article...' % cmi_debug )
                else:
                    logging.info('%s - REMOTE Hard-linked URL - NOT Extracting NEWS from article...' % cmi_debug )
            else:
                logging.info('%s - Not DEEP processing NEWS articles' % cmi_debug )
                print ( "DEBUG: Not doing DEEP data extraction of news article !")
                self.news_article_depth_1a()

        print ( " " )
        print ( "Main TOP level news page processed")
        print ( f"News articles evaluated: {x}")
        print ( f"Local URLs: {l_url} / Remote URLs: {r_url}" )
        return x        # number of NEWS articles discovered

    """
    #print ( f"== {erow}: == URL.div element: {a_subset[erow].name}" )
    # print ( f" / Date: {a_subset[erow].time.text}" )         # Pretty data
    # print ( f"== {erow}: == URL.div element: {a_subset[erow]}" )
    """

# method 3
    def extract_article_data(self, news_article_url):
        """A complex html DATA EXTRACTION. We are now getting into the dirty details"""
        """and low-levl data components/elements within specific HTML news data page."""
        """WARN: This is extremley specific to a single https://finance.yahoo.com news article."""

        cmi_debug = __name__+"::"+self.extract_article_data.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        right_now = date.today()
        a_subset = self.news_article_depth_1(news_article_url)      # got DEEP into this 1 news HTML page & setup data extraction zones
        print ( f"Tag sections in news page: {len(a_subset)}" )
        for erow in range(len(a_subset)):       # cycyle through tag sections in this dataset (not predictible or consistent)
            if a_subset[erow].time:     # if this element rown has a <time> tag...
                nztime = a_subset[erow].time['datetime']
                ndate = a_subset[erow].time.text
                dt_ISO8601 = datetime.strptime(nztime, "%Y-%m-%dT%H:%M:%S.%fz")
                # TODO: calculate age of this news article
                # TODO: parse out date component, subtract date from today, calculate num_of_days old
                if a_subset[erow].div:  # if this element row has a sub <div>
                    nauthor = a_subset[erow].div.find(attrs={'itemprop': 'name'}).text

            # DEBUG
            if self.args['bool_xray'] is True:        # DEBUG Xray
                taglist = []
                for tag in a_subset[erow].find_all(True):
                    taglist.append(tag.name)
                print ( "Unique tags:", set(taglist) )

            logging.info('%s - Cycle: Follow News deep URL extratcion' % cmi_debug )
        print ( f"Details: {ndate} / Time: {dt_ISO8601} / Author: {nauthor}" )
        days_old = (dt_ISO8601.date() - right_now)
        print ( f"News article age: DATE: {dt_ISO8601.date()} / TIME: {dt_ISO8601.time()} / AGE: {abs(days_old.days)}" )
        return

# method #3
# Hacking function - keep me arround for a while
    def prog_bar(self, x, y):
        """simple progress dialogue function"""
        if x % y == 0:
            print ( " " )
        else:
            print ( ".", end="" )
        return

# method #4
    def topg_listall(self):
        """Print the full DataFrame table list of Yahoo Finance Top Gainers"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.topg_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.n_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 15 gainers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.n_df1.drop(self.n_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        self.n_df1 = self.n_df0.sort_values(by='Pct_change', ascending=False ).head(15).copy(deep=True)    # create new DF via copy of top 10 entries
        self.n_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.n_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.n_df1.sort_values(by='Pct_change', ascending=False ).head(15) )
        return