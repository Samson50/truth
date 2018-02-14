import sys
import time
import csv

from random import randint
from webDriver import Driver
#from dbPopulate import DBPopulate

def sanitize(text): 
    if '"' in text:
        text = ''.join(text.split('"'))
    return text


class BillScraper:
    def __init__(self, firstCon):
        self.firstCongress = firstCon
        #self.populator = DBPopulate()
        self.driver = Driver() 
        self.testing = False
        self.maxBill = 0

    def getAction(self, chamber):
        """Returns a list of actions for the bill"""
        """Most recent action at index 0"""
        actions = self.driver.find('//div[@id="allActions-content"]/table/tbody/tr') # AllActions (date and action, drop 'Action By:'
        retActs = []
        for action in actions:
            acts = action.xpath('td')
            date = acts[0].text.split("/")
            date = date[2][:4]+"-"+date[0]+"-"+date[1]
            if (len(acts) == 3):
                try:
                    action = acts[1].text[0]+" - "+acts[2].text.strip()
                except:
                    action = acts[2].text.strip()
                actBy = acts[2].xpath("span")[0].text#.strip()
                if actBy is None or "\n": actBy = ""
            else:
                action = chamber+" - "+acts[1].text.strip()
                actBy = acts[1].xpath("span")[0].text
                if actBy is None or "\n": actBy = ""
            retActs += [[date,action,actBy]]
        return retActs

    def getCosponsor(self):
        cospons = self.driver.find('//div[@id="cosponsors-content"]/div/table[1]/tbody/tr/td/a') # Cosponsors
        # Cosponsored date  = ...tbody/tr/td[2]
        retCospons = []
        if "Cosponsors Who Withdrew" in cospons:
            stopper = cospons.index("Cosponsors Who Withdrew")
            cospons = cospons[:stopper]
        for spon in cospons:
            leg = spon.text[5:].split(' [')[0]
            leg = " ".join(leg.split(', ')[::-1])
            #leg = leg.split(', ')[1]+" "+leg.split(', ')[0]
            fname = leg.split()[0]
            lname = sanitize(' '.join(leg.split()[1:]))
            ps = spon.text.split('[')[1].split('-')[0:2]
            retCospons += [[fname, lname, ps[0], ps[1]]]
            #self.populator.insertCosponsor(fname, lname, billID)
        return retCospons

    def getCommittees(self):
        committees = self.driver.find('//div[@id="committees-content"]/div/div/table/tbody/tr[@class="committee"]/th') # Committees
        return [x.text for x in committees]

    def getBillDetails(self, billID, chamber, conNum):
        realatedBills = self.driver.find('//div[@id="relatedBills-content"]/div/div/table/tbody/tr/td[1]/a') # RelatedBills
        subjects = self.driver.find('//div[@id="subjects-content"]/div/ul/li/a') # Policy Area
        actions = self.getAction(chamber)
        cosponsors = self.getCosponsor()
        committees = self.getCommittees()
        print cosponsors
        print committees
        #self.populator.insertLatest(billID, actions[0][0])
        #for bill in realatedBills:
        #    self.populator.insertRelatedBill(billID, bill.text.strip())
        #for subject in subjects:
        #    self.populator.insertBillPolicy(billID, subject.text.strip())
        #for action in actions:
        #   self.populator.insertAction(billID, action[0], action[1], action[2])
        #for cosponsor in cosponsors:
        #   self.populator.insertCosponsor(cosponsor[0], cosponsor[1], billID)
        #for committee in committees:
        #   self.populator.insertComboBill(billID, committee)

    def getType(self, bid):
        if 'house-bill' in bid: return 'H.R.'
        elif 'house-amendment' in bid: return 'H.Amdt.'
        elif 'house-resolution' in bid: return 'H.Res.'
        elif 'house-joint-resolution' in bid: return 'H.J.Res.'
        elif 'house-concurrent-resolution' in bid: return 'H.Con.Res.'
        elif 'senate-bill' in bid: return 'S.'
        elif 'senate-amendment' in bid: return 'S.Amdt.'
        elif 'senate-resolution' in bid: return 'S.Res.'
        elif 'senate-joint-resolution' in bid: return 'S.J.Res.'
        elif 'senate-concurrent-resolution' in bid: return 'S.Con.Res.'
        else: print("Can't find type for :"+bid)

    def billFromLink(self, billLink, conNum, billID):#Takes simple link to bill
        self.driver.fetch(billLink)
        billName = self.getType(billLink.split('/')[5])+billLink.split('/')[6]
        fname = ''
        lname = ''
        title = ''
        headers = self.driver.find('//div[@class="featured"]/div/div[@class="overview"]/table/tbody/tr')
        for head in headers:
            h = head.xpath('th')[0].text
            if 'Sponsor' in h:
                try:
                    sponsor = head.xpath('td/a')[0].text[5:].split(' [')[0]
                except:
                    sponsor = head.xpath('td')[0].text
                    break
                name = sponsor.split(', ')[1]+" "+sponsor.split(', ')[0]
                fname = name.split()[0]
                lname = sanitize(' '.join(name.split()[1:]))
        try:
            title = self.driver.find('//div[@id="titles_main"]/div/div/div/p')[0].text
        except:
            try: title = self.driver.find('//div[@id="content"]/div[@id="main"]/p')[0].text
            except: return
        try:
            title = sanitize(title.strip())
            if len(title) >= 255: title = title[0:253]
            #print billID, billName, fname, lname
            #print title
            if sponsor == '' and latest == '': return
            #self.populator.insertBill(billID, billName, conNum, fname, lname, title)
            #billID = self.populator.getBillID(billName, conNum)
            self.getBillDetails(billID, billName[0], conNum)
        except UnboundLocalError as e:
            print "Bill: "+billLink+" Error: "+str(e)

    def getConth(self, con):
        if (con%10 == 1): return str(con)+"st"
        if (con%10 == 2): return str(con)+"nd"
        if (con%10 == 3): return str(con)+"rd"
        else: return str(con)+"th"

    def getCongressFile(self, fcon, lcon):
        t_index = {0:'bill',1:'amendment',2:'resolution',3:'concurrent-resolution',4:'joint-resolution'}
        i = 0
        totTime = 0.0
        with open("conr"+str(fcon)+"-"+str(lcon)+".csv", "rb") as condat:
            conrows = csv.reader(condat)#, delimiter=' ', quotechar='|')
            for row in conrows:
                self.tdex = 0
                for cell in row:
                    m = int(cell)
                    if self.tdex > 4:
                        chamber = "house-"
                        b=1
                    else:
                        chamber = "senate-"
                        b=0
                    t = t_index[self.tdex-5*b]
                    if t == "amendment": billType = "amendment"
                    else: billType = "bill"
                    t = chamber + t
                    billID = (fcon+i)*100000+self.tdex*10000
                    n=1
                    currentBill = 1.0
                    for x in range(1,(m+1)):
                        if self.tdex == 9 and n == 1:
                            n = 34
                            currentBill = n*1.0
                        start = time.time()
                        self.billFromLink("https://www.congress.gov/"+billType+"/"+self.getConth(fcon+i)+"-congress/"+t+"/"+str(n)+"/all-info",fcon+i,billID+n)
                        end = time.time()
                        currentBill += 1
                        totTime += end-start
                        avgTime = totTime/(currentBill)#*1.0)
                        sys.stdout.write("\rProgress: [\%{0:2.1f}] {1}:{2} {3:4.2f}>\r".format(100*currentBill/m, str(self.tdex), str(currentBill), avgTime))
                        sys.stdout.flush()
                        n += 1
                    self.tdex += 1
                i += 1

    def getOneMax(self, congNum, chamber, t):
        if chamber: chamber = 'House'
        else: chamber = 'Senate'
        search = 'https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%5B%22'+str(congNum)+'%22%5D%2C%22chamber%22%3A%22'+chamber+'%22%2C%22type%22%3A%22'+t+'%22%7D'
        if self.testing: print search
        self.driver.fetch(search)
        try:
            ans = int(self.driver.find('//div[@id="main"]/ol/li/span/a')[0].text.split('.')[-1])
        except:
            ans = 0
        return ans

    def getMaxes(self, fcon, lcon): #should only need to run fully once
        types = [
                ['bills','amendments','resolutions','concurrent-resolutions','joint-resolutions'],
                ['bills','amendments','resolutions','concurrent-resolutions','joint-resolutions']
                ]
        t_index = {'bills':0,'amendments':1,'resolutions':2,'concurrent-resolutions':3,'joint-resolutions':4}
        vals = {i : list(types) for i in range(lcon,fcon-1,-1)}
        mat = [[0 for x in range(10)] for y in range(lcon-fcon+1)]
        while len(vals.keys()) != 0 :
            k = vals.keys()[randint(0,len(vals.keys())-1)]
            if len(vals[k][0]) != 0 and len(vals[k][1]) != 0: c = randint(0,1)
            elif len(vals[k][1]) == 0: c = 0
            else: c = 1
            try:
                i = randint(0,len(vals[k][c])-1)
            except:
                i = 0
            mat[lcon-k][t_index[vals[k][c][i]]+5*c] = self.getOneMax(k,c,vals[k][c][i])
            w = list(vals[k][c])
            del w[i]
            vals[k][c] = w
            if len(vals[k][0]) == 0 and len(vals[k][1]) == 0:
                del vals[k]
        with open("conr"+str(fcon)+"-"+str(lcon)+".csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(mat)


    def runTest(self):
        self.getCongressFile(114,114)

    def close(self):
        self.driver.quit()

test = BillScraper(107)
test.testing = True
run = time.time()
test.runTest()
end = time.time()
print "Test completed in %0.3f seconds." % ((end-run))
test.close()

print "Exiting"
print "Closed"
