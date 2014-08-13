""" A library to scrape ASP.NET generated pages from http://www.izbori.ba """

import re

import lxml.html
import mechanize


class Page(object):

    user_agent = ('User-agent',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0')
    host = ('Host', 'www.izbori.ba')

    def __init__(self, url=None):
        self.browser = mechanize.Browser()
        self.browser.addheaders = [self.user_agent, self.host]

    def get(self, url):
        """ Get a page from an url """
        response = self.browser.open(url)
        self.html = response.read()

        hrefs = self.get_links(self.html)

        for i in hrefs:
            match = re.match(".*?('(.*?)','(.*?)')", i)
            url_value = match.group(2)

            self.browser.select_form(name='aspnetForm')
            self.browser.form.set_all_readonly(False)
            self.browser['__EVENTTARGET'] = url_value
            self.browser['__EVENTARGUMENT'] = ''
            response = self.browser.submit()

            a = open('%s.html' % url_value, 'w')
            a.write(response.read())
            a.close()

            print '%s.html created' % url_value

    def get_links(self, html):
        """ Find all urls on page """
        tree = lxml.html.fromstring(html)
        href = tree.xpath("//a/@href")

        return href
