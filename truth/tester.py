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