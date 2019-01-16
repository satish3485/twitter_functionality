import pymongo
from datetime import timedelta, datetime
from flask import Flask, session, request

# Run flask app
app = Flask(__name__)

 # setup database Mongodb
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]

 #  check if values is none
def  checkItNone(first, second):
    if first is None or first == '' or second is None or second == '':
        return True
# ============================Basic Functionality===============================
# session expire in 5 minutes
# this function accept post method and it is user login required username and password
@app.route('/login', methods = ['POST'])
def login():
    if 'username' in session:
        username = session['username']
        return 'Logged in as ' + username + '<br>' + "Please log out first"
    try:
        userName =  request.form['username']
        userPassword = request.form['password']
    except:
        userName =  None
        userPassword = None

    checker = checkItNone(userName,userPassword)
    if checker:
        return "You missed parameter username or password"
    query = { "userName": userName, "userPassword": userPassword}
    global db
    collection = db["user"]
    result = collection.find_one(query)
    if result is None:
        return 'User Name or Password are incorrect, try again'
    else:
        session['username'] = userName
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        return 'Hello, '+ userName

# this function accept post method and it is user signup required username and password
@app.route('/signup', methods = ['POST'])
def signUp():
    if 'username' in session:
        username = session['username']
        return 'Logged in as ' + username + '<br>' + "Please log out first"

    try:
        userName =  request.form['username']
        userPassword = request.form['password']
    except:
        userName =  None
        userPassword = None

    checker = checkItNone(userName,userPassword)
    if checker:
        return "You missed parameter username or password"
    global db
    collection = db["user"]
    query = { "userName": userName}
    result = collection.find_one(query)
    if result is None:
        userData = { "userName": userName, "userPassword": userPassword, "follow":[], "tweet":[], "like":[], "unlike":[], 'messages':[] }
        x = collection.insert_one(userData)
        return 'You are successfully signup'
    else:
        return 'User Name alredy taken'

# this function accept get method and it is user logout
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        return "You are successfully logout."
    return "You are not Log In."
# ============================End Basic Functionality===============================
# ============================Extended Functionality===============================
# this function accept post method and it is user follow to another user required username
@app.route('/follow', methods = ['POST'])
def follow():
   if 'username' in session:
       try:
           userName =  request.form['username']
       except:
           userName =  None

       checker = checkItNone(userName,1)
       if checker:
           return "You missed parameter username"
       global db
       collection = db["user"]
       query = { "userName": userName}
       result = collection.find_one(query)
       if result is None:
           return "No user with this User Name "
       userData = { "userName": session['username']}
       x = collection.find_one(userData)
       if userName == session['username']:
           return "You can not follow yourself."
       if result['_id'] in x['follow']:
            return "You are already follow "+ userName
       collection.update_one(userData, {'$push': {'follow': result['_id']}})
       return 'You are successfully following'
   else:
       return "You are not Log In. You can not follow"

# this function accept post method and it is user unfollow to another user required username
@app.route('/unfollow', methods = ['POST'])
def unfollow():
   if 'username' in session:
        try:
            userName =  request.form['username']
        except:
            userName =  None

        checker = checkItNone(userName,1)
        if checker:
            return "You missed parameter username"
        global db
        collection = db["user"]
        query = { "userName": userName}
        result = collection.find_one(query)
        if result is None:
            return "No user with this User Name "
        userData = { "userName": session['username']}
        x = collection.find_one(userData)
        if userName == session['username']:
           return "You can not unfollow yourself."
        if result['_id'] in x['follow']:
            x['follow'].remove(result['_id'])
            collection.update_one(userData, {'$set': {'follow': x['follow']}})
            return 'You are successfully unfollow'
        else:
            return "You are not follow "+ userName
   else:
       return "You are not Log In. You can not follow"

# this function accept get method to see user following and tweet
@app.route('/')
def allData():
   if 'username' in session:
       global db
       collection = db["user"]
       query = { "userName": session['username']}
       result = collection.find_one(query)
       if result is None:
           return "No user with this User Name "
       userData = result['follow']
       userTweet = result['tweet']
       followerList = " following :\n "
       for i in userData:
           x = collection.find_one({'_id':i})
           followerList +=  x['userName'] +" \n"
       followerList += " tweets : \n"
       for i in userTweet:
           tweetCollection = db['tweet']
           x = tweetCollection.find_one({'_id':i})
           followerList +=  x['title']+"  &nbsp &nbsp "+x['message'] +"  &nbsp &nbsp "+str(x['date']).split('.')[0]+" \n"
       return followerList
   else:
       return "You are not Log In. You can not follow"

# this function accept post method and it is create tweet required title and message
@app.route('/create', methods = ['POST'])
def createTweet():
   if 'username' in session:
       try:
           title = request.form['title']
           tweet = request.form['message']
       except:
           title = None
           tweet = None

       checker = checkItNone(title,tweet)
       if checker:
           return "You missed parameter title or message"
       global db
       collection = db["user"]
       tweetCollection = db['tweet']
       query = { "userName": session['username']}
       result = collection.find_one(query)
       tweetResult = tweetCollection.find_one({'title':title})
       if result is None:
           return "You are not Log In. You can not tweet"
       for i in result['tweet']:
           if tweetResult is not None and i == tweetResult['_id']:
               return "Please change the title, because it is alrady used"
       userData = { "title":title,"message": tweet, "date":datetime.now(), "userId":result['_id'], 'retweet':[], 'likes': 0}
       x = tweetCollection.insert_one(userData)
       collection.update_one(query, {'$push': {'tweet': x.inserted_id}})
       return 'You tweet succesfully'
   else:
     return "You are not Log In. You can not tweet"

# this function accept post method and it is read tweet required title
@app.route('/read', methods = ['POST'])
def readTweet():
   if 'username' in session:
       try:
           title = request.form['title']
       except:
           title = None

       checker = checkItNone(title,1)
       if checker:
           return "You missed parameter title"
       global db
       collection = db["user"]
       tweetCollection = db['tweet']
       tweetResult = tweetCollection.find_one({'title':title})
       if tweetResult is not None:
           x = "tweet :\n"+tweetResult['title']+" "+tweetResult['message'] +" "+str(tweetResult['date']).split('.')[0]
           return x
       return " There are not tweet with title "+ title
   return "You are not Log In. You can not read tweet"

# this function accept post method and it is delete tweet required title
@app.route('/delete', methods = ['POST'])
def deleteTweet():
   if 'username' in session:
       try:
           title = request.form['title']
       except:
           title = None
       checker = checkItNone(title,1)
       if checker:
           return "You missed parameter title"
       global db
       collection = db["user"]
       tweetCollection = db['tweet']
       query = { "userName": session['username']}
       result = collection.find_one(query)
       tweetResult = tweetCollection.find_one({'title':title})
       if result is None:
           return "You are not Log In. You can not tweet"
       if tweetResult is None:
           return "No tweet with this title "
       if tweetResult['_id'] in result['tweet']:
           if tweetResult['userId'] == result['_id']:
               result['tweet'].remove(tweetResult['_id'])
               collection.update_one(query, {'$set': {'tweet':result['tweet']}})
               tweetCollection.delete_one({'title':title})
               return 'You are successfully delete tweet'
           else:
              return "You can not delete this tweet"
       else:
           return "You do not have this tweet"
   else:
       return "You are not Log In. You can not delete tweet"

# ============================End Extended Functionality===============================

# ============================Extra Credit===============================
# this function accept post method and it is like tweet required title
@app.route('/like', methods = ['POST'])
def likeTweet():
   if 'username' in session:
       try:
           title = request.form['title']
       except:
           title = None

       checker = checkItNone(title,1)
       if checker:
           return "You missed parameter title"
       global db
       collection = db["user"]
       tweetCollection = db['tweet']
       query = { "userName": session['username']}
       result = collection.find_one(query)
       tweetResult = tweetCollection.find_one({'title':title})
       if result is None:
           return "You are not Log In. You can not tweet"
       if tweetResult is None:
           return "No tweet with this title "
       print(tweetResult['_id'])
       if tweetResult['_id'] in result['like']:
           return "You already liked this tweet"
       if tweetResult['_id'] in result['unlike']:
           result['unlike'].remove(tweetResult['_id'])
           collection.update_one(query, {'$set': {'unlike':result['unlike']}})
       tweetCollection.update_one(tweetResult, {'$set': {'likes':(tweetResult['likes']+1)}})
       collection.update_one(query, {'$push': {'like': tweetResult['_id']}})
       return 'You are successfully liked tweet'
   else:
       return "You are not Log In. You can not delete tweet"
# this function accept post method and it is unlike tweet required title
@app.route('/unlike', methods = ['POST'])
def unlikeTweet():
   if 'username' in session:
       try:
           title = request.form['title']
       except:
           title = None

       checker = checkItNone(title,1)
       if checker:
           return "You missed parameter title"
       global db
       collection = db["user"]
       tweetCollection = db['tweet']
       query = { "userName": session['username']}
       result = collection.find_one(query)
       tweetResult = tweetCollection.find_one({'title':title})
       if result is None:
           return "You are not Log In. You can not tweet"
       if tweetResult is None:
           return "No tweet with this title "
       if tweetResult['_id'] in result['unlike']:
           return "You already unliked this tweet"
       if tweetResult['_id'] in result['like']:
           result['like'].remove(tweetResult['_id'])
           collection.update_one(query, {'$set': {'like':result['like']}})
       tweetCollection.update_one(tweetResult, {'$set': {'likes':(tweetResult['likes']-1)}})
       collection.update_one(query, {'$push': {'unlike': tweetResult['_id']}})
       return 'You are successfully unliked tweet'
   else:
       return "You are not Log In. You can not delete tweet"
# this function accept post method and it is retweet tweet required title and message
@app.route('/retweet', methods = ['POST'])
def reTweet():
   if 'username' in session:
       try:
           title = request.form['title']
           tweet = request.form['message']
       except:
           title = None
           tweet = None

       checker = checkItNone(title,tweet)
       if checker:
           return "You missed parameter title or message"

       global db
       collection = db["user"]
       tweetCollection = db['tweet']
       query = { "userName": session['username']}
       result = collection.find_one(query)
       tweetResult = tweetCollection.find_one({'title':title})
       if result is None:
           return "You are not Log In. You can not tweet"
       userData = { "message": tweet, "date":datetime.now(), "userId":result['_id'], 'retweet':[]}
       tweetCollection.update_one(tweetResult, {'$push': {'retweet': userData}})
       return 'You retweet succesfully'
   else:
     return "You are not Log In. You can not tweet"
# this function accept post method and it is reply required username and message
@app.route('/reply', methods = ['POST'])
def reply():
   if 'username' in session:
       try:
           username = request.form['username']
           tweet = request.form['message']
       except:
           username  = None
           tweet = None

       checker = checkItNone(username,tweet)
       if checker:
           return "You missed parameter title or message"

       global db
       collection = db["user"]
       replydb = db["reply"]
       query = { "userName": session['username']}
       result = collection.find_one(query)
       replyTo = collection.find_one({'userName': username})
       if result is None:
           return "You are not Log In. You can not tweet"
       if replyTo is None:
           return "This user does not exist"
       userData = { "message": tweet, "date":datetime.now(), 'messageFrom':result['_id'], 'messageTo':replyTo['_id']}
       x = replydb.insert_one(userData)
       collection.update_one(query, {'$push': {'messages': x.inserted_id}})
       collection.update_one(replyTo, {'$push': {'messages': x.inserted_id}})
       return 'You reply succesfully'
   else:
     return "You are not Log In. You can not tweet"

# ============================End Extra Credit===============================
if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug = True)
