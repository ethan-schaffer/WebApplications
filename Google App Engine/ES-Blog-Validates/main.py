import webapp2
import cgi
import re
import random
import string
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])
#Ugly Code Above

PASS_RE = re.compile(r"[\S]{3,20}$")
USER_RE = re.compile(r"[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r"[a-z|A-z]{3,20}\@[a-z|A-z]{3,20}\.[a-z|A-z]{3}$")

global user
def make_salt(length):
    key = ''
    for i in range(length):
        key += random.choice(string.lowercase + string.uppercase + string.digits)
    return key

def make_pw_hash(name, pw, salt=None):
	return hash_str(name + pw + salt)+"|"+salt

def valid_pw(name, pw, h):


#Added From Cookies 3#
def hash_str(s):
    SECRET = "imsosecret"
    return hmac.new(SECRET,str(s)).hexdigest()

def make_secure_val(s):
    return str(s)+"|"+str(hash_str(s))

def check_secure_val(h):
    if make_secure_val(get_unhashed(h)) == h:
#    if hash_str(h) == make_secure_val(get_unhashed(h)):
        return get_unhashed(h)
    return None

def get_unhashed(s):
    return str(s).split('|', 1)[0]
#Added From Cookies 3#


class User(db.Model):
    username = db.StringProperty()
    password = db.TextProperty()
    email = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)

def valid_email(email):
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


class MainPage(webapp2.RequestHandler):
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
		template_values = {"user": user,
		                   "pass": pw,
		                   "email": em,
		                   "userRW": userRW,
		                   "passRW": passRW,
		                   "emailRW": emailRW}
		template = JINJA_ENVIRONMENT.get_template('index.html')
		if((ug and pg and eg)):
			self.redirect('/Success')
		else:
			self.response.write(template.render(template_values))

class Success(webapp2.RequestHandler):
	def get(self):
		global user
		template_values = {"User": user}
		template = JINJA_ENVIRONMENT.get_template('success.html')
		self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
 ('/', MainPage),
 ('/Success', Success)
], debug=True)