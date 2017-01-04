import webapp2
import cgi
import re
import random
import string
import time
import jinja2
import os
import hashlib
import hmac
import logging
from google.appengine.ext import db

global user
global error
error = False

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])
#Ugly Code Above

PASS_RE = re.compile(r"[\S]{3,20}$")
USER_RE = re.compile(r"[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r"[a-z|A-z]{3,20}\@[a-z|A-z]{3,20}\.[a-z|A-z]{3}$")

class MyHandler(webapp2.RequestHandler):
    def write(self, *writeArgs):    
        self.response.write(" : ".join(writeArgs))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
class User(db.Model):
    username = db.StringProperty()
    hashed_password = db.TextProperty()
    email = db.TextProperty()
    salt = db.TextProperty()
def make_salt(length):
    salt = ''
    for i in range(length):
        salt += random.choice(string.digits + string.uppercase + string.lowercase)
    return salt
def valid_pw(hashed, pw, salt):

	return (str(hashed) == str(hash_str(pw, salt)))
def get_unhashed(s):

    return str(s).split('&', 1)[0]
def get_hashed_bit(s):

    return str(s).split('&', 1)[1]
def get_user(userId):
	unhashed =str(get_unhashed(userId))
	return User.get_by_id(int(unhashed))
def is_cookie_good(userId):
	try:
		if(userId == 'none' or userId == ''):
			return False
		unhashed =str(get_unhashed(userId))
		userToWelcome = User.get_by_id(int(unhashed))
		if(str(hash_str(unhashed, 'secret') == get_hashed_bit(userId))):
			return True
		else:
			return False
	except:
		return False
	return False
def hash_str(password, salt):
	if type(salt) == unicode:
		salt = str(salt).encode()
	if type(password) == unicode:
		password = str(password).encode()
	return str(hmac.new(salt, password).hexdigest())
def valid_email(email):
	if(email == ''):
		return True
	return EMAIL_RE.match(email)
def escape_html(s):

    return cgi.escape(s, quote = True)
def is_username_good(username):
  if(USER_RE.match(username)):
    return True
  return False
def is_email_good(email):
  if(valid_email(email)):
    return True
  return False
def is_password_good(password, password2):
  if(password == password2 and PASS_RE.match(password)):
    return True
  return False

class Register(MyHandler):
	def get(self):
		template_values = {"user": "",
		                   "pass": "",
		                   "email": "",
		                   "userRW": "",
		                   "passRW": "",
		                   "emailRW": ""}
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

	def post(self):
		global user
		user = self.request.get("username")
		em = self.request.get("email")
		pw = self.request.get("password")
		pw2 = self.request.get("password2")
		ug = is_username_good(user)
		pg = is_password_good(pw, pw2)
		eg = is_email_good(em)
		userRW=""
		passRW=""
		emailRW=""
		if not ug:
			userRW = "Please Re-enter your username"
		if not pg:
			passRW = "Please Re-enter your passwords"
		if not eg:
			emailRW = "Please Re-enter your email"
		usersWithName = db.GqlQuery("SELECT * FROM User WHERE username = '%s' " % (user) )
		for u in usersWithName:
			userRW = "This username is already registered"
		template_values = {"user": user,
		                   "pass": pw,
		                   "email": em,
		                   "userRW": userRW,
		                   "passRW": passRW,
		                   "emailRW": emailRW}
		template = JINJA_ENVIRONMENT.get_template('index.html')
		if((userRW == "" and pg and eg)):
			userTemp = User()
			salt = make_salt(25)
			userTemp.username = user
			userTemp.hashed_password = hash_str(pw, salt)
			userTemp.email = em
			userTemp.salt = salt
			userTemp.put()
			time.sleep(0.2)
			valueToHash = str(userTemp.key().id())
			idVal = str(valueToHash) + "&" + str(hash_str(valueToHash, 'secret'))
			self.response.headers.add_header('Set-Cookie', 'user_id=%s' % idVal)
			self.redirect('/blog/Success')
		else:
			self.response.write(template.render(template_values))
class Success(MyHandler):
	def get(self):
		userId = self.request.cookies.get('user_id', 'none') 
		if(not is_cookie_good(userId)):
			self.redirect('/blog/badcookie/')
			return
		try:
			userToWelcome = get_user(userId)
		except:
			self.redirect('/blog/badcookie/')
			return
		template_values = {"User": userToWelcome.username}
		template = JINJA_ENVIRONMENT.get_template('success.html')
		self.response.write(template.render(template_values))
class Welcome(MyHandler):
	def get(self):
		userId = self.request.cookies.get('user_id', 'none') 
		if(not is_cookie_good(userId)):
			self.redirect('/blog/badcookie/')
			return
		try:
			userToWelcome = get_user(userId)
		except:
			self.redirect('/blog/badcookie/')
			return
		template_values = {"User": userToWelcome.username}
		template = JINJA_ENVIRONMENT.get_template('success.html')
		self.response.write(template.render(template_values))

class Login(MyHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('login.html')
		template_values = {"successfulYN": ""}
		self.response.write(template.render(template_values))

	def post(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=none')
		usernameInput = self.request.get("username")
		passwordInput = self.request.get("password")
		template_values = {"successfulYN": usernameInput}
		users = "That username doesn't exist"
		usernames = db.GqlQuery("SELECT * FROM User WHERE username = '%s' " % (str(usernameInput)) )
		good = False
		for u in usernames:
			userToTest = u
			good = True
			users = "Sorry " + u.username + ", your password is incorrect"
		if(good):
			if (userToTest.hashed_password == str(hash_str(passwordInput, userToTest.salt.encode()))):
				user = userToTest.username
				valueToHash = str(userToTest.key().id())

				idVal = str(valueToHash) + "&" + str(hash_str(valueToHash, 'secret'))

				self.response.headers.add_header('Set-Cookie', 'user_id=%s' % idVal)
				self.redirect('/blog/Welcome')
				return
		template_values = {"successfulYN": users}
		template = JINJA_ENVIRONMENT.get_template('login.html')
		self.response.write(template.render(template_values))
class Logout(MyHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=')
		time.sleep(.2)
		self.redirect('/blog/Login')
		return
class Scold(MyHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('scold.html')
		self.response.write(template.render())
class WeGotLost(MyHandler):
	def get(self, extrawhatever):
		template = JINJA_ENVIRONMENT.get_template('home.html')
		self.response.write(template.render())
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('home.html')
		self.response.write(template.render())
class BlogPost(db.Model):
    subject = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
class BlogHome(MyHandler):
    def get(self):
		userId = self.request.cookies.get('user_id', 'none')
		posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC limit 10")
		dictionary = {"posts": posts, "Title": "Ethan's Blog!"}
		self.render('posts.html', **dictionary)

    def post(self):
        self.redirect('/blog/')
class WriteABlogPost(MyHandler):
    def get(self):
		userId = self.request.cookies.get('user_id', 'none') 
		if(not is_cookie_good(userId)):
			self.redirect('/blog/badcookie')
		global error
		errorMessage = ("Uh oh, that's not quite right" if error else "")
		dictionary = {"ph_subject": "Your Subject Here", "ph_content": "Your Post Here", "ph_error": errorMessage}
		self.render('newpost.html', **dictionary)

    def post(self):
		userId = self.request.cookies.get('user_id', 'none') 
		if(not is_cookie_good(userId)):
			self.redirect('/blog/badcookie')
		temp = BlogPost()
		temp.subject = self.request.get("subject")
		temp.content = self.request.get("content")
		time.sleep(.2)
		if (temp.subject) and (temp.content):
			temp.put()
			time.sleep(.2)
			error = False
			logging.info("**** L O G ******")
		else:
			error = True
		if error:
			self.redirect('/blog/register')
		self.redirect('/blog/'+str(temp.key().id()))


class SinglePost(MyHandler):
    def get(self, blogid):
		logging.info("*************** SinglePost.get ****************")
		post = BlogPost.get_by_id(int(blogid))
		dictionary = {"post": post, 
						"Title": "Ethan's new blog"}
		self.render('post.html', **dictionary)

    def post(self, blogid):
		post = BlogPost.get_by_id(int(blogid))
		dictionary = {"post": post, 
					"Title": "Ethan's new blog"}
		self.render('post.html', **dictionary)

application = webapp2.WSGIApplication([
 (r'/blog/register\/{0,1}', Register),
 (r'/blog/Register\/{0,1}', Register),

 ('/blog/Success', Success),
 ('/blog/Welcome', Welcome),

 (r'/blog/login\/{0,1}', Login),
 (r'/blog/Login\/{0,1}', Login),

 (r'/blog/logout\/{0,1}', Logout),
 (r'/blog/Logout\/{0,1}', Logout),

 (r'/blog/badcookie\/{0,1}', Scold),


 (r'/blog\/{0,1}', BlogHome),
 (r'/blog/(\d+)', SinglePost),
 (r'/blog/newpost\/{0,1}', WriteABlogPost),

 ('/', WeGotLost),
 (r'/blog/(\S+)', WeGotLost),

], debug=True)