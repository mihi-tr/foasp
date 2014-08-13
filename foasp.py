""" A library to scrape ASP.NET generated pages """

import requests
import lxml.html
import urlparse
import re

class Page():
    def __init__(self,request=None):
        if request is not None:
            self.request=request
            self.html=request.text
            self.cookies=dict(request.cookies.items())
            self.parse_html()

    def get(self,url):
        """ Get a page from an url """
        r = requests.get(url)
        self.request=r
        self.html=r.text
        self.cookies=dict(r.cookies.items())
        self.parse_html()

    def getfirst(self,xpath):
        ret = self.tree.xpath(xpath)
        if len(ret):
            return ret[0]
        else:
            return ""

    def parse_html(self):
        """ parse the html of the page  -- also set the required state"""
        self.tree = lxml.html.fromstring(self.html)
        hidden=self.tree.xpath("//input[@type='hidden']/@name")
        self.params=dict([(i,self.getfirst("//input[@name='%s']/@value"%i))
            for i in hidden])
        self.action=self.getfirst("//form[@name='aspnetForm']/@action")
        self.action=urlparse.urljoin(self.request.url,self.action)
    
    def follow(self,href):
        """ Follow a link:
            usually this comes as
            javascript:__doPostBack('event','eventvalue')"""
        match=re.match(".*?('(.*?)','(.*?)')",href)
        event=match.group(2)
        eventargument=match.group(3)
        params=dict(self.params.items())
        params.update(
                {
                "ctl00$sc1": event,
                "__EVENTTARGET":event,
                "__EVENTARGUMENT":eventargument,
                "__ASYNCPOST":"false",
                })
        r=requests.post(self.action,data=params,cookies=self.cookies)        
        return Page(request=r)
