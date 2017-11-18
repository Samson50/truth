import os
import sys
import time
#import platform
#import urllib

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
#from time import accept2dyear

# http://clerk.house.gov/evs/2015/index.asp

class VoteScraper:
    def __init__(self):
        print "VoteScraper Initializing"
        os.environ['MOZ_HEADLESS'] = '1'
        print "os.environ['MOZ_HEADLESS'] = '1'"
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        print "binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)"
        self.driver = webdriver.Firefox(firefox_binary=binary)
        
    def fetch(self, string):
        print '\n'#"Retrieving: "+string
        self.driver.get(string)

    def findElements(self, code, search):
        print '\n'#"Finding element: "+search
        return self.driver.find_elements(code, search)

    def getText(self, elem):
        return ''.join(elem.get_property('textContent').strip())
    
    def addRoll(self, year, voteNum, issue, question, date, SoH):
        if SoH == 'S':
            vid = year*1000000+voteNum*10+1
        else:
            vid = year*1000000+voteNum*10+0
        print date 
        print str(year)+": VID - "+str(vid)+" Issue: "+issue
        print question 
        
    def addVotes(self, votes, year, voteNum, SoH):
        if SoH == 'S':
            vid = year*1000000+voteNum*10+1
        else:
            vid = year*1000000+voteNum*10+0
        if SoH == 'S':
            print "Senate: Votes for %d, vote ID %d: %d" % (year, vid, len(votes))
        if SoH == 'H':
            print "House: Votes for %d, vote ID %d: %d" % (year, vid, len(votes))
        #print votes 
    
    def getVotesHouse(self, year, rollNum):
        self.fetch('http://clerk.house.gov/evs/'+str(year)+'/roll'+str(rollNum).zfill(3)+'.xml')
        alot = self.findElements('xpath', '//body')
        info = alot[0].text.split('\n')[3:7]
        date = alot[0].text.split('\n')[3].split('      ')[3]
        choices = alot[0].text.split('----')[1:]
        question = ''
        issue = ''
        for i in info:
            i=i.strip()
            if 'QUESTION:' in i:
                question = i.split(':  ')[1].strip()
            if (i.startswith('H ')):# and 'R' in i):
                issue = '.'.join(i.split('  ')[0].split())
            elif i.startswith('S '):
                issue = '.'.join(i.split('  ')[0].split())
        votes = {}
        for x in range(0, len(choices)):
            w = [z.strip() for z in choices[x].split('---')]
            if 'YEAS' in w[0] or 'AYES' in w[0]:
                votes.update(dict((v,'Yea') for v in w[1].split('\n')))
            elif 'NAYS' in w[0] or 'NOES' in w[0]:
                votes.update(dict((v,'Nay') for v in w[1].split('\n')))
            elif 'NOT VOTING' in w[0] or 'ANSWERED':
                votes.update(dict((v,'Not Voting') for v in w[1].split('\n')))
            else:
                print 'SPECIAL CASE! SPECIAL CASE! YEAR %d ROLL %d'%(year, rollNum)
                print w
        self.addRoll(year, rollNum, issue, question, date, 'H')
        self.addVotes(votes, year, rollNum, 'H')
        
    def getRollHouse(self, year):
        self.fetch('http://clerk.house.gov/evs/'+str(year)+'/index.asp')
        maxRoll = int(self.findElements('xpath', '//table/tbody/tr[2]/td/a')[0].text)
        for roll in range(maxRoll-5, maxRoll+1):
            self.getVotesHouse(year, roll) 
        
    def getVotesSenate(self, con, sess, vote):
        self.fetch("https://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress="+str(con)+"&session="+str(sess)+"&vote="+str(vote).zfill(5))
        votes = self.findElements('xpath', "//main/div/div[@class='newspaperDisplay_3column']/span")[0].text.split('\n')
        votes = dict((x.split(', ')[0],x.split(', ')[1]) for x in votes)
        info = self.findElements('xpath', '//div[@id="secondary_col2"]/div[1]/div')
        question = ''
        issue = ''
        date = ''
        for x in info:
            if 'Question:' in x.text:
                question = x.text.split(': ')[1]
            if 'Measure Number:' in x.text:
                issue = x.text.split(': ')[1]
            if 'Vote Date:' in x.text:
                date = x.text.split(': ')[1]
                date = date.split()[1][:-1]+'-'+date.split()[0][:3]+'-'+date.split()[2][:-1]
        year = 1901+con+sess 
        self.addRoll(year, vote, issue, question, date, 'S')
        self.addVotes(votes, year, vote, 'S')

    
    def getRollSenate(self, con, sess):
        self.fetch("https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_"+str(con)+"_"+str(sess)+".htm")
        vote = self.findElements('xpath', '//div[@id="secondary_col2"]/table/tbody/tr[1]/td[1]/a')
        maxVote = int(vote[0].text.split()[0])
        for vote in range(maxVote-5, maxVote+1):
            self.getVotesSenate(con, sess, vote)

    
    def printInfo(self, ans):
        for x in ans:
            print(self.getText(x))
    
    def runTest(self):
        self.getRollSenate(115, 1)
        self.getRollHouse(2017)

    def close(self):
        self.driver.quit()
        
test = VoteScraper()
run = time.time()
test.runTest()
end = time.time()
print "Test completed in %0.3f seconds." % ((end-run))
test.close()

print "Exiting"
print "Closed"

