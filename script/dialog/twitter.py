# Voice Twitter for Spoken Language Processing
# May 9, 2012
# Yufei Liu (yl2515)
# Aneem Talukder (aft2108)

import os
import re
import sys
import random
import socket
import tweepy
import httplib
import time
import datetime
from datetime import timedelta

token_dir = "tokens/"
groups_dir = "groups/"
logs_dir = "logs/"
sentence_dir = "/tmp/"
tts_base = "/proj/speech/users/cs4706/yl2515/"
asr_base = "/proj/speech/users/cs4706/asrhw/yl2515/"
tts = "perl " + tts_base + "timeline.pl"
asr = "python " + asr_base + "asr.py"

#todo: check for 64bits (only gatto)
rec = "python /proj/speech/tools/autorecord/record.py"
if socket.gethostname().split('.')[0]=="gatto":
  rec = "python /proj/speech/tools/autorecord-64bit/record.py"

welcome_message = ['prompt0000','Welcome to Voice Twitter!']
choose_action = ['question0000','What would you like to do?']
choose_action_help = ['help0000',"You can say read tweets, write a tweet, or exit. At any time, say MAIN MENU to go to main menu."]
choose_read_type = ['question0001',"What kind of tweets do you want to listen to?"]
choose_read_type_help = ['help0001',"You can say read tweets in my timeline or in a category such as entertainment or trends. You can also specify a preset group of users as a source, or provide a time range. For example: read tweets in my timeline in colleagues in the last ten hours. For detailed instruction, please read the attached documentation."]
choose_tweet_action = ['question0002',"What would you like to do to this tweet?"]
choose_tweet_action_help = ['help0002',"Say retweet, favorite, follow, unfollow, or say next tweet or nothing to skip. You can optionally say two commands at once. For example, retweet and follow this user"]
choose_tweet_type = ['question0003',"What would you like to tweet?"]
choose_tweet_type_help = ['help0003',"You can say tweet followed by a topic, which can be about a random fact or the weather. Or you can tweet about your emotions. You can also specify a future tweet. For example, tweet that I am sad in one hour. Read the documentation for detailed instructions."]
bye = ['prompt0002',"Thanks, goodbye!"]
sorry = ['prompt0001',"Sorry I didn't quite get that, try again"]


choose_action_help_played = False
choose_read_type_help_played = False
choose_tweet_action_help_played = False
choose_tweet_type_help_played = False

if (len(sys.argv) > 1 and sys.argv[1] == "--nohelp"):
  choose_action_help_played = True
  choose_read_type_help_played = True
  choose_tweet_action_help_played = True
  choose_tweet_type_help_played = True

# get user name
handle = raw_input("Please enter your twitter handle, without @: ").strip()
os.system("cp " + groups_dir + "__sample " + groups_dir + handle)
#handle = "italktweets"
consumer_key = "JSwUZoRIH2Av2kjjojRY3w"
consumer_secret = "FYTb3aj0irEn4yWVugvrzHVaLf44ncntLwhfcWwOSM"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
access_key = ""
access_secret = ""



stamp = str(round(time.time()))
current_log = logs_dir + "yl2515" + stamp[0:len(stamp)-2] + ".txt"
current_log_wav_dir = logs_dir + "yl2515" + stamp[0:len(stamp)-2] + "/"
os.system("mkdir " + current_log_wav_dir)
wav_counter_in = 1
wav_counter_out = 1

if os.path.exists(token_dir + handle):
  print "Welcome back, @" + handle + "!\n"
  f = open(token_dir + handle, 'r')
  access_key = f.readline().strip()
  access_secret = f.readline().strip()
else:
  print "You need to authorize your account for Voice Twitter\n"
  auth_url = auth.get_authorization_url()
  os.system("firefox " + auth_url)
  verifier = raw_input("Please enter the verification code: ").strip()
  auth.get_access_token(verifier)
  access_key = auth.access_token.key
  access_secret = auth.access_token.secret
  f = open(token_dir + handle, 'w')
  f.write(access_key + "\n" + access_secret)


auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

#print str(len(api.home_timeline(count=100))) + " tweets \n\n"

#for tweet in api.home_timeline(count=100):
#  print tweet.text + "\n"


# 0 - initial state, welcome message
# 1 - main menu, choose action
# 2 - read tweets
# 3 - interact with individual tweets
# 4 - write tweets
state=None
state_desc = ["Welcome", "Main menu", "Reading tweets", "Interact with individual tweets", "Writing tweets"]

def get_groups(index):
  counter = 0
  for line in open(groups_dir + handle, 'r'):
    if (line[0]=="#"):
      continue
    line = line[0:len(line)-1]
    if counter == index:
      return line.split(",")
    counter = counter + 1

def get_raw_feed(dom, fil, time_fil):
  tweets = None
  if dom == "TIMELINE":
    tweets = api.home_timeline()
  elif dom == "TRENDS":
    trends = api.trends_daily()
    queries = re.findall("'query': '([^']+)'",str(trends))
    tweets = api.search(" OR ".join(queries[0:5]))
  else:
    tweets = api.search(dom)
  result_tweets = []
  for t in tweets:

    username = ""
    user_id = 0
    if dom == "TIMELINE":
      username = t.user.screen_name
      user_id = t.user.id
    else:
      username = t.from_user
      user_id = t.from_user_id

    if (username == handle):
      continue
    if (fil != None and not (username.lower() in fil)):
      continue
    if (time_fil != None and t.created_at < time_fil):
      continue
    result_tweets.append({"text":t.text,"screen_name":username,"created_at":t.created_at,"id":t.id,"user_id":user_id})
  return result_tweets


def get_feed(tweets):
  #first element is the summary json, need to be removed prior to reading individual tweets
  to_return = []
  temp = '{type: "read",tweets: ['

  atLeastOneTweet = False

  for t in tweets:
    to_return.append('{type: "tweet",text: "From ' + preprocess(t["screen_name"]) + ', ' + preprocess(t["text"]) +'"}')
    atLeastOneTweet = True
    tmpStr = str(time.mktime(t["created_at"].timetuple()))
    timestamp = tmpStr[0:len(tmpStr)-2]
    temp += '{text: "This is a Tweet!",id: 1324123,timestamp: ' + timestamp + ',user: "yufeiliu",user_id: 3123,original_user: "yufeiliu",original_user_id: 1234},'

  if atLeastOneTweet:
    temp = temp[0:len(temp)-1]
  temp += "]}"

  to_return.insert(0, temp)

  return to_return

def preprocess(tweet):
  result = tweet.replace('"', '')
  result = result.replace("I'm", "I am")
  result = result.replace("'", '')
  result = result.replace(" #", " .. hashtag ")
  result = result.replace("RT", " ree-tweet...")
  result = result.replace(" @", " twitter handle.. ")
  result = result.replace(" http://", " HTTP colon slash slash ")
  result = unicode(result)
  return result.encode('ascii','ignore')

def confirm(what):
  return '{type: "action",action: "' + what + '"}'

def pack(what):
  return "'" + what + "'"

def tmp_name():
  return "/tmp/wav_" + str(random.randrange(10000,99999)) + ".wav"

def read_static(what):
  global wav_counter_out
  os.system("play static/" + what[0] + ".wav")
  os.system("cp static/" + what[0] + ".wav " + current_log_wav_dir + "SysOutput" + str(wav_counter_out) + ".wav")
  log("System: " + what[1])
  log("System output file at " + current_log_wav_dir + "SysOutput" + str(wav_counter_out) + ".wav\n")
  wav_counter_out = wav_counter_out + 1

def read(what):
  global wav_counter_out
  tmp_file = tmp_name()
  os.system(tts + " " + pack(what) + " " + tmp_file)
  os.system("play " + tmp_file)
  os.system("cp " + tmp_file + " " + current_log_wav_dir + "SysOutput" + str(wav_counter_out) + ".wav")
  os.system("rm -rf " + tmp_file)
  fi = open(sentence_dir + "temp.txt", 'r')
  log("System: " + fi.readline())
  log("System output file at " + current_log_wav_dir + "SysOutput" + str(wav_counter_out) + ".wav\n")
  wav_counter_out = wav_counter_out + 1

'''
def say(what):
  BASEDIR = "/proj/speech/users/cs4706/yl2515/partc"
  wav_file_name = tmp_name()
  speech_file_name = tmp_name()
  speech_file = open(speech_file_name, "w")
  speech_file.write('(load "'+BASEDIR+'/festvox/SLP_timeline_xyz_ldom.scm")' + "\n")
  speech_file.write('(voice_SLP_timeline_xyz_ldom)' + "\n")
  speech_file.write('(Parameter.set \'Audio_Method \'Audio_Command)' + "\n")
  speech_file.write('(Parameter.set \'Audio_Required_Rate 16000)' + "\n")
  speech_file.write('(Parameter.set \'Audio_Required_Format \'wav)' + "\n")
  speech_file.write('(Parameter.set \'Audio_Command "cp $FILE ' + wav_file_name + '")' + "\n")
  speech_file.write('(SayText "' + what + '")' + "\n")
  os.system("cd " + BASEDIR + "; festival --batch " + speech_file_name)
  print "cd " + BASEDIR + "; festival --batch " + speech_file_name
  print wav_file_name
  print speech_file_name
  exit()
  os.system("play " + wav_file_name)
  os.system("rm -fr " + wav_file_name)
  os.system("rm -fr " + speech_file_name)
'''

def get_grammar():
  if state==1:
    return "4"
  else:
    return str(state-1)

def get():
  global wav_counter_in
  os.system(rec)
  os.system("cp output.wav " + current_log_wav_dir + "UserInput" + str(wav_counter_in) + ".wav")
  output = os.popen(asr + " output.wav " + get_grammar())
  wav_counter_in = wav_counter_in + 1
  lines = ""

  flag = 0
  while 1:
    line = output.readline()
    if "<BEGIN>" in line:
      flag = 1
      continue
    if "<END>" in line:
      break

    if flag==1:
      lines += line + "\n"

  m = re.search("::::([^:]+)::::",lines)
  if (m!=None):
    log("User: " + m.group(1))
  log("User input file at " + current_log_wav_dir + "UserInput" + str(wav_counter_in) + ".wav")
  m = re.search("-----([^-]+)-----",lines)
  if (m!=None):
    concepts = m.group(1).replace("\t","").replace(":","=").replace("\n",",")
    log("Semantics [" + concepts + "]\n")
  return lines


def random_fact():
  h = httplib.HTTPConnection("www.reddit.com")
  h.request("GET","/r/todayilearned/.rss")
  r = h.getresponse()
  body = r.read()
  tils = re.findall("<title>TIL ([^<>]+)</title>",body)
  for til in tils:
    if (len(til)<=140):
      return til
  return tils[0][0:135] + "..."

def weather():
  h = httplib.HTTPConnection("www.google.com")
  h.request("GET","/ig/api?weather=" + api.me().location.replace(" ", "+"))
  r = h.getresponse()
  body = r.read()
  temperature = re.search('<current_conditions>.*temp_f data="([0-9]+)".*</current_conditions>',body).group(1)
  condition = re.search('<current_conditions>.*<condition data="([^"]+)".*</current_conditions>',body).group(1)
  return "Weather in " + api.me().location + " is " + condition + ", " + temperature + " degrees!"

def log(what):
  tmp_file = open(current_log, "a")
  tmp_file.write(what + "\n")

def change_state(new_state):
  global state
  state = new_state
  log("\n\nState is now: " + state_desc[state] + "\n\n")

log(str(datetime.datetime.fromtimestamp(time.time())))
log("Logged in with Twitter handle @" + handle)


FRIENDS=get_groups(0)
FAMILY=get_groups(1)
COLLEAGES=get_groups(2)
CELEBRITIES=get_groups(3)
OTHERS=get_groups(4)

change_state(0)

while True:
  if state==0:
    read_static(welcome_message)
    change_state(1)
    continue
  elif state==1:
    read_static(choose_action)
    if (choose_action_help_played == False):
      choose_action_help_played = True
      read_static(choose_action_help)
    lines = get()

    if "not recognized" in lines:
      read_static(sorry)
      continue
    elif "HELP ME" in lines:
      read_static(choose_action_help)
      continue

    if "LEAVE" in lines or "QUIT" in lines or "EXIT" in lines:
      read_static(bye)
      break
    elif "READ" in lines or "LISTEN" in lines:
      change_state(2)
      continue
    elif "WRITE" in lines:
      change_state(4)
      continue
    elif "HELP" in lines:
      #todo
      print "NO HELP FOR YOU!"
      break
  elif state==2:
      read_static(choose_read_type)
      if choose_read_type_help_played==False:
        read_static(choose_read_type_help)
        choose_read_type_help_played = True
      lines = get()

      print lines

      if "not recognized" in lines:
        read_static(sorry)
        continue
      elif "HELP ME" in lines:
        read_static(choose_read_type_help)
        continue

      if "MAIN MENU" in lines:
        change_state(1)
        continue

      group_filter = None
      cutoff = None
      domain = None

      m = re.search("Time:[\t ]+([^\n]+)",lines)
      if (m!=None and m.group(1)!="Unknown"):
        timestr = m.group(1).replace("IN THE LAST ","")

        unitnum = 1
        if "FIVE" in timestr:
          unitnum = 5
        if "TEN" in timestr:
          unitnum = 10
        if "TWENTY" in timestr:
          unitnum = 20
        if "THIRTY" in timestr:
          unitnum = 30

        now = datetime.datetime.now()
        cutoff = None
        if "HOUR" in timestr:
          cutoff = now - timedelta(hours=unitnum)
        if "MINUTE" in timestr:
          cutoff = now - timedelta(minutes=unitnum)
        if "DAY" in timestr:
          cutoff = now - timedelta(days=unitnum)

      if "POLITICS" in lines:
        domain = "POLITICS"
      elif "SPORTS" in lines:
        domain = "SPORTS"
      elif "ENTERTAINMENT" in lines:
        domain = "ENTERTAINMENT"
      elif "NEWS" in lines:
        domain = "NEWS"
      elif "TRENDS" in lines:
        domain = "TRENDS"
      else:
        domain = "TIMELINE"
        group_filter = None

        if "FRIENDS" in lines:
          group_filter = FRIENDS
        elif "FAMILY" in lines:
          group_filter = FAMILY
        elif "COLLEAGUES" in lines:
          group_filter = COLLEAGUES
        elif "CELEBRITIES" in lines:
          group_filter = CELEBRITIES
        elif "OTHERS" in lines:
          group_filter = OTHERS

      raw_tweets = get_raw_feed(domain,group_filter,cutoff)
      tweets = get_feed(raw_tweets)
      summary = tweets.pop(0)
      change_state(3)
      read(summary)
      i = -1


      for tweet in tweets:
        i = i + 1
        print "*** About to read: " + tweet
        read(tweet)
        read_static(choose_tweet_action)
        action_lines = get()
        if "not recognized" in action_lines:
          read_static(sorry)
          action_lines = get()
        if "HELP ME" in action_lines:
          read_static(choose_tweet_action_help)
          action_lines = get()

        if "MAIN MENU" in action_lines:
          change_state(1)
          break
        if "NEXT" in action_lines:
          continue
        if "UNFOLLOW" in action_lines:
          #need to reload timeline, and remember where you were
          api.destroy_friendship(raw_tweets[i]["user_id"])
          read(confirm("unfollow"))
        if "FOLLOW" in action_lines and not ("UNFOLLOW" in action_lines):
          api.create_friendship(raw_tweets[i]["user_id"])
          read(confirm("follow"))
        if "RETWEET" in action_lines:
          api.retweet(raw_tweets[i]["id"])
          read(confirm("retweet"))
        if "FAVORITE" in action_lines:
          api.create_favorite(raw_tweets[i]["id"])
          read(confirm("favorit"))
      change_state(1)
  elif state==4:
    read_static(choose_tweet_type)
    if choose_tweet_type_help_played == False:
      read_static(choose_tweet_type_help)
      choose_tweet_type_help_played = True
    lines = get()

    if "not recognized" in lines:
      read_static(sorry)
      continue
    elif "HELP ME" in lines:
      read_static(choose_tweet_type_help)
      continue

    if "MAIN MENU" in lines:
      change_state(1)
      continue
    elif "ANGRY" in lines:
      api.update_status("I am " + "angry!")
    elif "SAD" in lines:
      api.update_status("I am " + "sad :(")
    elif "HAPPY" in lines:
      api.update_status("I am " + "happy! :)")
    elif "EXCITED" in lines:
      api.update_status("I am " + "excited! :D")
    elif "RANDOM" in lines:
      api.update_status(random_fact())
    elif "WEATHER" in lines:
      api.update_status(weather())

    #todo: future tweet

    read('{type: "action",action: "tweet"}')
    #todo: add question for whether to tweet again
    change_state(1)

print "done!"

