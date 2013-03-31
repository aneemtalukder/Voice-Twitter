#ASR concept extractor
#By Yufei Liu and Aneem Talukder
#April 13, 2012
#Spoken Language Processing
import re
import sys
import os

if (len(sys.argv)<3):
  print "Enter the wav file name followed by grammar number as arguments. Example: test1.wav 1"
  exit()

p = os.popen('/proj/speech/users/cs4706/pasr/recognize_wav.py ' + sys.argv[1] + ' -g /proj/speech/users/cs4706/asrhw/yl2515/gram' + sys.argv[2] + '.jsgf -a 3 -d /proj/speech/users/cs4706/asrhw/yl2515/wlist5o.dic')
resultLine = None
while 1:
  line = p.readline()
  if not line: break
  if 'ASR Result:' in line:
    resultLine = line
    break

def pack(arr, name, space = 1, optional=1):
  temparr = []
  for a in arr:
    temparr.append("(" + a + ")")
  return '(?P<' + name + '>' + (" " if space==1 else "") + "(" + '|'.join(temparr) + '))' + ("?" if optional==1 else "")


# gram1
category = ["POLITICS", "SPORTS", "ENTERTAINMENT", "NEWS", "TRENDS"]
domain = ["IN MY TIMELINE"]

for cat in category:
  domain.append("IN " + cat)

number = ["FIVE", "TEN", "TWENTY", "THIRTY"]
duration = ["MINUTE", "HOUR", "DAY"]

for num in number:
  for unit in ["MINUTES", "HOURS", "DAYS"]:
    duration.append(num + " " + unit)

time = []
for dur in duration:
  time.append("IN THE LAST " + dur)

groupname = ["FRIENDS", "FAMILY", "COLLEAGUES", "CELEBRITIES", "OTHERS"]
group = []

for gr in groupname:
  group.append("IN " + gr)

mainmenu = "MAIN MENU"

query1 = '(READ TWEETS' + pack(domain, "sDomain") + pack(time, "sTime") + pack(group, "sGroup") + ')|(' + mainmenu + ')|(HELP ME)'


#gram2
action = '(((FAVORITE)|(RETWEET))( ((THIS TWEET)|(THIS)))?)|(((FOLLOW)|(UNFOLLOW)) THIS USER)'
query2 = '(NEXT TWEET)|((I WANT TO )?(?P<action1>('+action+'))( AND (?P<action2>('+action+')))?)|('+mainmenu+')|(HELP ME)'


#gram3
futuretime = ["NOW"]

duration2 = ["ONE MINUTE", "ONE HOUR", "ONE DAY"]

for num in number:
  for unit in ["MINUTES", "HOURS", "DAYS"]:
    duration2.append(num + " " + unit)


for dur in duration2:
  futuretime.append("IN " + dur)

topic = "(ABOUT ((A RANDOM FACT)|(THE WEATHER)))|(THAT I AM ((ANGRY)|(HAPPY)|(SAD)|(EXCITED)))"
query3 = "((I WANT TO )?TWEET( (?P<topic>("+topic+")))"+pack(futuretime,"time")+")|("+mainmenu+")|(HELP ME)"

#gram4
prefix = "(((I WANT TO)|(I WOULD LIKE TO)|(CAN I)) )?"
query4 = "("+prefix+"WRITE A TWEET)|(((READ)|(" + prefix + "LISTEN TO)) TWEETS)|((EXIT)|(QUIT)|(LEAVE))|(HELP ME)"

def cleanse(s):
  return s[s.find("'")+1:s.find("',")]

print "<BEGIN>"

def parse(s, gram):
  if gram==1:
    m = re.match(query1, s)
    sType = None
    sDomain = None
    sTime = None
    sGroup = None

    if "HELP ME" in s:
      print "-----"
      print "Grammar:\t1"
      print "Help: true"
      print "-----"
    elif (m != None and m != False and s == m.group(0)):
      if s==mainmenu:
        sType = mainmenu
      else:
        sType = "READ TWEETS"
      sDomain = m.group("sDomain")
      sTime = m.group("sTime")
      sGroup = m.group("sGroup")
      print "-----"
      print "Grammar:\t1"
      print "Type:\t\t" + (sType if sType!=None else "Unknown")
      print "Domain:\t\t" + (sDomain if sDomain!=None else "Unknown")
      print "Time:\t\t" + (sTime if sTime!=None else "Unknown")
      print "Group:\t\t" + (sGroup if sGroup!=None else "Unknown")
      print "-----"
    else:
      print "Sentence '" + s + "' not recognized in grammar " + str(gram)
  elif gram==2:
    sType = None
    sAction1 = None
    sAction2 = None
    m = re.match(query2, s)
    if "HELP ME" in s:
      print "-----"
      print "Grammar:\t2"
      print "Help: true"
      print "-----"
    elif (m == None):
      print "Type:\t\tNEXT TWEET"
    elif (m != False and s == m.group(0)):
      if s==mainmenu:
        sType = mainmenu
      elif s=="NEXT TWEET":
        sType = "NEXT TWEET"
      else:
        sType = "ACTION"
      sAction1 = m.group("action1")
      sAction2 = m.group("action2")
      print "-----"
      print "Grammar:\t2"
      print "Type:\t\t" + (sType if sType!=None else "Unknown")
      print "Action1:\t" + (sAction1.split(" ")[0] if sAction1!=None else "Unknown")
      print "Action2:\t" + (sAction2.split(" ")[0] if sAction2!=None else "Unknown")
      print "-----"
    else:
      print "Sentence '" + s + "' not recognized in grammar " + str(gram)
  elif gram==3:
    sType = None
    sTopic = None
    sTime = None
    m = re.match(query3, s)
    if "HELP ME" in s:
      print "-----"
      print "Grammar:\t3"
      print "Help: true"
      print "-----"
    elif (m!= None and m != False and s == m.group(0)):
      if s==mainmenu:
        sType = mainmenu
      else:
        sType = "TWEET"
      sTopic = m.group("topic")
      sTime = m.group("time")
      print "-----"
      print "Grammar:\t3"
      print "Type:\t\t" + (sType if sType!=None else "Unknown")
      print "Topic:\t\t" + (sTopic if sTopic!=None else "Unknown")
      print "Time:\t\t" + (sTime[1:] if sTime!=None else "Unknown")
      print "-----"
    else:
      print "Sentence '" + s + "' not recognized in grammar " + str(gram)
  elif gram==4:
    m = re.match(query4, s)
    if "HELP ME" in s:
      print "-----"
      print "Grammar:\t4"
      print "Help: true"
      print "-----"
    elif (m!= None and m != False and s == m.group(0)):
      print "-----"
      print "Grammar:\t4"
      print "Action:\t" + s
      print "-----"
    else:
      print "Sentence '" + s + "' not recognized in grammar " + str(gram)

print "::::" + cleanse(resultLine) + "::::"
parse(cleanse(resultLine), int(sys.argv[2]))

print "<END>"
