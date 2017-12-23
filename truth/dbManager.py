import mysql.connector
import sys

class DBManager:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='bob', password='bobwhite', host='localhost', database='federal')
        self.cursor = self.cnx.cursor()
        self.committees = ['Ways and Means','Judiciary','Energy and Commerce','Education and the Workforce','Natural Resources','Foreign Affairs','Transportation and Infrastructure','Financial Services','Oversight and Government Reform','Post Office and Civil Service','Rules','Armed Services','Agriculture','Veterans\' Affairs','Administration','Science, Space, and Technology','Merchant Marine and Fisheries','Appropriations','Small Business','Budget','Homeland Security','District of Columbia','Intelligence (Permanent)','Ethics','Joint Atomic Energy','Internal Security','Committees','Outer Continental Shelf','Energy (Ad Hoc)','Joint Deficit Reduction','Finance','Judiciary','Energy and Natural Resources','Health, Education, Labor, and Pensions','Commerce, Science, and Transportation','Homeland Security and Governmental Affairs','Environment and Public Works','Foreign Relations','Banking, Housing, and Urban Affairs','Agriculture, Nutrition, and Forestry','Rules and Administration','Armed Services','Indian Affairs','Budget','Appropriations','Small Business and Entrepreneurship','Post Office and Civil Service','Intelligence','District of Columbia','Aeronautical','Aging','Ethics','Senate Narcotics Caucus','Joint Deficit Reduction','Impeachment','Official Conduct','POW/MIA Affairs','Whitewater','Joint Economic','Joint Library','Joint Printing','Joint Taxation','Democratic Whip','Majority Whip','Assistant Democratic Leader','Majority Leader','Democratic Leader','The Speaker','International Relations','Government Reform','Resources','Science','Governmental Affairs','Permanent Select Committee on Intelligence']
        self.policyAreas = ['Agriculture and Food','Animals','Armed Forces and National Security','Arts, Culture, Religion','Civil Rights and Liberties, Minority Issues',
                            'Commerce','Congress','Crime and Law Enforcement','Economics and Public Finance','Education','Emergency Management','Energy','Environmental Protection',
                            'Families','Finance and Financial Sector','Foreign Trade and International Finance','Government Operations and Politics',
                            'Health','Housing and Community Development','Immigration','International Affairs','Labor and Employment','Law',
                            'Native Americans','Public Lands and Natural Resources','Science, Technology, Communications','Social Sciences and History',
                            'Social Welfare','Sports and Recreation','Taxation','Transportation and Public Works','Water Resources Development']

    def createLegis(self):
        try:
            legis_table =   ("CREATE TABLE Legislator ("
                                "LegID int auto_increment primary key,"
                                "FirstName char(60),"
                                "LastName char(60),"
                                "Party char(1),"
                                "State char(2),"
                                "Job char(1),"
                                "First int,"
                                "Website char(255),"
                                "PicURL char(255),"
                                "cid int"
                                ");"
                            )
            self.cursor.execute(legis_table)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def createMoney(self):
        try:
            money_table =   ("CREATE TABLE Money ("
                                "MonID int auto_increment primary key,"
                                "LegID int,"
                                "ContID int,"
                                "Cycle int,"
                                "Nature int,"
                                "Amount int"
                                ");"
                            )
            self.cursor.execute(money_table)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def createContributor(self):
        try:
            money_table =   ("CREATE TABLE Contributor ("
                                "ContID int auto_increment primary key,"
                                "Name char(100),"
                                "Type int"
                                ");"
                            )
            self.cursor.execute(money_table)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def createVote(self):
        try:
            vote_table =   ("CREATE TABLE Vote ("
                                "VoteID int auto_increment primary key,"
                                "Choice char(3),"
                                "VoteNum int," # year*1000000+voteNum*10+1
                                "LegID int"
                                ");"
                            )
            self.cursor.execute(vote_table)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createRoll(self):
        try:
            roll_table =   ("CREATE TABLE Roll ("
                                "RollID int auto_increment primary key,"
                                "VoteNum int," # year*1000000+voteNum*10+1
                                "Question char(255),"
                                "VoteDate DATE,"
                                "Issue int" #References BillID
                                ");"
                            )
            self.cursor.execute(roll_table)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def createBill(self):
        try:
            arguments =   ("CREATE TABLE Bill ("
                                "BillID int not null primary key,"#Change to int notnull
                                "Name char(20),"
                                "Congress int,"
                                "Sponsor int," # References LegID
                                "LastDate DATE,"
                                "Summary char(255)"
                                #"FullText TEXT" #MAX: 9457090 MED 16,777,215
                                #"FullText ???"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def insertCommittee(self, name):
        try:
            argument = "INSERT INTO Committee (ComName) VALUES (\""+name+"\");"
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def populateCommittee(self):
        for name in self.committees:
            self.insertCommittee(name)

    def createComm(self):
        try:
            arguments =   ("CREATE TABLE Committee ("
                                "ComID int auto_increment primary key,"
                                "ComName char(100)"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])
        self.populateCommittee()

    def insertPolicyArea(self, name):
        try:
            argument = "INSERT INTO PolicyArea (PAName) VALUES (\""+name+"\");"
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def populatePolicyArea(self):
        for name in self.policyAreas:
            self.insertPolicyArea(name)

    def createPolicyAreas(self):
        try:
            arguments =   ("CREATE TABLE PolicyArea ("
                                "PolID int auto_increment primary key,"
                                "PAName char(100)"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
            self.populatePolicyArea()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createBillPolicy(self):
        try:
            arguments = ("CREATE TABLE BillPolicy ("
                            "BPID int auto_increment primary key,"
                            "PolID int,"
                            "BillID int"
                            ");")
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createCosponsor(self):
        try:
            arguments =   ("CREATE TABLE Cosponsor ("
                                "CosID int auto_increment primary key,"
                                "BillID int,"
                                "LegID int"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createAction(self):
        try:
            arguments =   ("CREATE TABLE Action ("
                                "ActionID int auto_increment primary key,"
                                "ActionDate DATE,"
                                "ActionBy char(100),"
                                "BillID int,"
                                "ActionStr char(255)"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createCombo(self):
        try:
            arguments =   ("CREATE TABLE Combo ("
                                "ComboID int auto_increment primary key,"
                                "LegID int,"
                                "ComID int"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createComboBill(self):
        try:
            arguments =   ("CREATE TABLE ComboBill ("
                                "ComboID int auto_increment primary key,"
                                "BillID int,"
                                "ComID int"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def createRelatedBill(self):
        try:
            arguments =   ("CREATE TABLE RelatedBill ("
                                "RelatedID int auto_increment primary key,"
                                "BillID int,"
                                "RBName char(20)"
                                ");"
                            )
            self.cursor.execute(arguments)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk"+str(sys.exc_info()[0])

    def show(self, item):
        self.cursor.execute("select * from %s"%(item))
        for item in self.cursor.fetchall():
            print item

    def drop(self, table):
        if table == 'all':
            self.cursor.execute("show tables")
            for t in self.cursor.fetchall():
                self.cursor.execute("drop table %s"%(t))
                self.cnx.commit()
        else:
            self.cursor.execute("drop table %s"%(table))
            self.cnx.commit()

    def createAll(self):
        print "Creating Tables"
        self.createCombo()
        self.createAction()
        self.createBill()
        self.createComm()
        self.createCosponsor()
        self.createLegis()
        self.createRoll()
        self.createVote()
        self.createRelatedBill()
        self.createComboBill()
        self.createBillPolicy()
        self.createPolicyAreas()
        self.createMoney()
        self.createContributor()
        print "All Tables Created"

    def recreateAll(self):
        print "Dropping all tables"
        self.drop('all')
        print "Tables Dropped"
        self.createAll()

    def close(self):
        self.cursor.close()
        self.cnx.close()



test = DBManager()
test.drop('bill')
#test.drop('roll')
test.createBill()
#test.createRoll()
#test.recreateAll()
#test.close()
#test.createComm()
#test.populateCommittee()
#test.show('committee')
test.close()











#END
