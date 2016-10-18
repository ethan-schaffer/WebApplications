import webapp2
import cgi
import re

form = """
<head>
<link rel="stylesheet" type="text/css" href="stylesheets/style.css">
</head>

<body>
<h1> Please Enter your Info </h1>
<form method="post" action="/">
<div id="b">
<label> username <input type="text" name="username"   value="%(username)s"> 
<label> <br> password  <input type="text" name="password"  value="%(password)s">
<label> <br> comfirm password  <input type="text" name="password2" </label>
<label> <br> email (optional) <input type="text" name="email" value="%(email)s"> 
</div>
</label> <div style="color: red">%(error_u)s</div>
</label> <div style="color: red">%(error_p)s</div>
</label> <div style="color: red">%(error_e)s</div>

<input type="submit">
</form>
</body>
"""
PASS_RE = re.compile(r"[\S]{3,20}")
USER_RE = re.compile(r"[a-z|A-z|1-9|\_\-]{3,20}")
EMAIL_RE = re.compile(r"[a-z|A-z]{3,20}\@[a-z|A-z]{3,20}\.[a-z|A-z]{1,3}")
global user
def valid_email(email):
  return EMAIL_RE.match(email)
def escape_html(s):
    return cgi.escape(s, quote = True)

def write_form(self, email="", username="", password="", error_u="", error_e="", error_p=""):
  self.response.write(form % {"email": email, "username": username, "password": password, 
    "error_e": error_e, "error_p": error_p, "error_u": error_u})

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
    self.response.headers['Content-Type'] = 'text/html'
    #self.response.write("<h1>Welcome!</h1>")
    write_form(self)

  def post(self):
      global user
      user = self.request.get("username")
      em = self.request.get("email")
      pw = self.request.get("password")
      pw2 = self.request.get("password2")
      ug = is_username_good(user)
      eg = is_email_good(em)
      pg = is_password_good(pw, pw2)

      if(ug and eg and pg):
        self.redirect('/Success')
      else:
        write_form(self, escape_html(em), escape_html(user), escape_html(pw),
          "" if ug else "Please re-enter your Username", "" if eg else "Please re-enter your Email", "" if pg else "Please re-enter your Password")

class Success(webapp2.RequestHandler):
  def get(self):
    global user
    goodwork = """
    <h3>Well done, %(user)s</h3>
    """
    imageRecall = """
    <img src="images/success.png">
    """
    self.response.write("<h1>Good Work!</h1>")
    self.response.write(goodwork % {"user": user})
    self.response.write(imageRecall)

application = webapp2.WSGIApplication([
 ('/', MainPage),
 ('/Success', Success)
], debug=True)