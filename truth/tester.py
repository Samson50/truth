import requests

from lxml import html
from lxml.etree import tostring
ans = requests.get("http://www.opensecrets.org/members-of-congress/summary?cid=N00032019&cycle=2018&type=C")
#print ans.content
tree = html.fromstring(ans.content)
#bill = '.'.join(tree.xpath("//body")[0].text.split())
print tostring(tree)
#people = tree.xpath('//members/member')
#votes = tree.xpath('//members/member/vote_cast')
#date = tree.xpath('//vote_date')[0].text
#question = tree.xpath('//vote_question_text')[0].text
#issue = tree.xpath('//document_name')
#if len(issue):
#    issue = tree.xpath('//amendment_number')[0].text
#print date
#print question
#print issue
#print people[0].xpath('first_name')[0].text
#print votes[0].text#tostring(votes[0])
#print tostring(tree)

"""
import os, sys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
import requests

from lxml import html

#os.environ['MOZ_HEADLESS'] = '1'
#binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
#driver = webdriver.Firefox(firefox_binary=binary)
driver = webdriver.PhantomJS()

#driver.get('https://www.congress.gov/bill/115th-congress/senate-bill/2021/all-info')
#print driver.page_source

driver.get('https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D')
tree = html.fromstring(driver.page_source)

print "Start"

boxes = tree.xpath('//li[@class="expanded"]//div[@class="quick-search-member"]')
for box in boxes:
    data = box.xpath('div/span')
    for dat in data:
        da = dat.getchildren()
        if 'Served:' in da[0].text:
            for d in da[1].getchildren()[0].getchildren():
                print d.text#.split()[1].split('-')[0]
                #d.text.split()[1].split('-')[0]
        else:
            print da[0].text.strip()[:-1]
            print da[1].text.strip()
        #print html.tostring(da)[:100].strip()
        print "*"

print "End"
"""
