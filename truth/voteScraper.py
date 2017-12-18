import os
import sys
import requests
import time

from lxml import html, etree
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from dbPopulate import DBPopulate
#from time import accept2dyear

# http://clerk.house.gov/evs/2015/index.asp

class VoteScraper:
    def __init__(self):
        self.populator = DBPopulate()
        self.max = 0
        self.current = 0
        self.driver = webdriver.PhantomJS()
        
    def fetch(self, string):
        print "Retrieving: "+string
        self.driver.get(string)
        #self.tree = html.fromstring(self.driver.page_source)

    def findElements(self, code, search):
        #print '\n'#"Finding element: "+search
        return self.driver.find_elements(code, search)
    
    def getSpecial(self, string):
        self.driver.get(string)
        page = self.driver.page_source
        page = page.split('?>')[1]
        self.tree = html.fromstring(page)
    
    def get(self, string):
        #print string
        page = requests.get(string)#, header)
        self.tree = html.fromstring(page.content)
        time.sleep(3.0)
    
    def find(self, string):
        return self.tree.xpath(string)

    def getText(self, elem):
        return ''.join(elem.get_property('textContent').strip())
    
    def addRoll(self, year, voteNum, issue, question, date, SoH):
        if SoH == 'S':
            vid = year*1000000+voteNum*10+1
        else:
            vid = year*1000000+voteNum*10+0
        #issue = '.'.join(issue.split())
        #print vid, question
        self.populator.insertRoll(vid, question, issue)
        
    def addVotes(self, votes, year, voteNum, SoH):
        if SoH == 'S':
            vid = year*1000000+voteNum*10+1
        else:
            vid = year*1000000+voteNum*10+0
        for name in votes.keys():
            state = ''
            fname = ''
            lname = ''
            voter = name #Should be votes.keys()
            if '(' in name: # "lastname, firstname (P-ST)"
                name = voter.split(' (')[0]
                state = voter.split(' (')[1][:-1]
                if '-' in state: state = state.split('-')[1]
            if ',' in name:
                name = name.split(', ')[1]+' '+name.split(', ')[0]
                fname = name.split()[0]
                lname = ' '.join(name.split()[1:])
            else:
                lname = name
            #print fname+"--"+lname
            #print vid, votes[voter], fname, lname, state, SoH
            self.populator.insertVote(vid, votes[voter], fname, lname, state, SoH)
    
    def getVotesHouse(self, year, rollNum):
        self.get('http://clerk.house.gov/evs/'+str(year)+'/roll'+str(rollNum).zfill(3)+'.xml')
        try:
            issue = self.find('//legis-num')[0].text
        except:
            return
        if issue == "JOURNAL": return 
        if issue is not None: issue = '.'.join(issue.split()).title()
        else: return
        people = self.find('//recorded-vote/legislator')
        vote = self.find('//recorded-vote/vote')
        question = self.find('//vote-question')[0].text
        date = self.find('//action-date')[0].text
        votes = {}
        for x in range(0, len(people)):
            person = people[x].get('unaccented-name')
            if (' (' not in person):
                person = person+" ("+people[x].get('party')+"-"+people[x].get('state')+")"
            votes[person] = vote[x].text
        self.addRoll(year, rollNum, issue, question, date, 'H')
        self.addVotes(votes, year, rollNum, 'H')
        
    def getRollHouse(self, year):
        self.fetch('http://clerk.house.gov/evs/'+str(year)+'/index.asp')
        maxRoll = int(self.findElements('xpath', '//table/tbody/tr[2]/td/a')[0].text)
        self.max = maxRoll
        self.current = 0
        totTime = 0
        for roll in range(1, maxRoll+1):
            start = time.time()
            self.getVotesHouse(year, roll) 
            end = time.time()
            self.current += 1
            totTime += end-start
            avgTime = totTime/(self.current*1.0)
            sys.stdout.write("\rProgress: [\%{0:2.1f}] {1} {2:4.2f}>\r".format(100*self.current/self.max, str(self.current), avgTime))
            sys.stdout.flush()
        
    def getVotesSenate(self, con, sess, vote):
        self.getSpecial("https://www.senate.gov/legislative/LIS/roll_call_votes/vote"+str(con)+str(sess)+"/vote_"+str(con)+"_"+str(sess)+"_"+str(vote).zfill(5)+".xml")
        #self.fetch("https://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress="+str(con)+"&session="+str(sess)+"&vote="+str(vote).zfill(5))
        #votes = self.findElements('xpath', "//main/div/div[@class='newspaperDisplay_3column']/span")[0].text.split('\n')
        #votes = dict((x.split(', ')[0],x.split(', ')[1]) for x in votes)
        #info = self.findElements('xpath', '//div[@id="secondary_col2"]/div[1]/div')
        #question = ''
        #issue = ''
        #date = ''
        people = self.find('//members/member')
        votes_cast = self.find('//members/member/vote_cast')
        try:
            date = self.find('//vote_date')[0].text
        except:
            print etree.tostring(self.tree)
        date = date.split()[1][:-1]+'-'+date.split()[0][:3]+'-'+date.split()[2][:-1]
        question = self.find('//vote_question_text')[0].text
        issue = self.find('//document_name')[0]
        if issue.text is None: 
            issue = self.find('//amendment_number')[0]
            if issue.text is None: 
                issue = ''
            else: 
                issue = issue.text
        else: issue = issue.text
        if len(issue) > 0: issue = ''.join(issue.split())
        votes = {}
        for x in range(0,len(people)):
            fname = people[x].xpath('first_name')[0].text
            lname = people[x].xpath('member_full')[0].text
            name = ' '.join(lname.split()[:-1])+", "+fname+" "+lname.split()[-1]
            votes[name] = votes_cast[x].text
        year = 1901+con+sess 
        #if len(issue) == 0:
        #    return 
        self.addRoll(year, vote, issue, question, date, 'S')
        self.addVotes(votes, year, vote, 'S')
    
    def getRollSenate(self, con, sess):
        self.fetch("https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_"+str(con)+"_"+str(sess)+".htm")
        vote = self.findElements('xpath', '//div[@id="secondary_col2"]/table/tbody/tr[1]/td[1]/a')
        maxVote = int(vote[0].text.split()[0])
        self.max = maxVote
        totTime = 0
        for vote in range(1, maxVote+1):
            start = time.time()
            self.getVotesSenate(con, sess, vote)
            end = time.time()
            self.current += 1
            totTime += end-start
            avgTime = totTime/(self.current*1.0)
            sys.stdout.write("\rProgress: [\%{0:2.1f}] {1} {2:4.2f}>\r".format(100*self.current/self.max, str(self.current), avgTime))
            sys.stdout.flush()

    
    def printInfo(self, ans):
        for x in ans:
            print(self.getText(x))
    
    def runTest(self):
        self.getRollSenate(114, 1)
        self.getRollHouse(2015)

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

