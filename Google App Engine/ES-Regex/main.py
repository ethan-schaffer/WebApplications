import webapp2
import cgi

form = """
<p> Please Enter your info </p>
<form method="post" action="/">

<label> username   <input type="text" name="username"   value="%(username)s"> </label> <div style="color: red">%(error_u)s</div>
<label> <br> password  <input type="text" name="password"  value="%(password)s"> </label> <div style="color: red">%(error_p)s</div>
<label> <br> comfirm password  <input type="text" name="password2" </label>
<label> <br> email (optional) <input type="text" name="email" value="%(email)s"> </label> <div style="color: red">%(error_e)s</div>

<input type="submit">
</form>
"""

def escape_html(s):
    return cgi.escape(s, quote = True)

def write_form(self, email="", username="", password="", error_u="", error_e="", error_p=""):
  self.response.write(form % {"email": email, "username": username, "password": password, 
    "error_e": error_e, "error_p": error_p, "error_u": error_u})

def is_username_good(username):
  return False

def is_email_good(email):
  return False

def is_password_good(password, password2):
  if(password == password2):
    return True
  return False

class MainPage(webapp2.RequestHandler):

  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write("<h1>Welcome!</h1>")
    write_form(self)

  def post(self):
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
    self.response.write("<h`>Good Work!</h1>")


application = webapp2.WSGIApplication([
 ('/', MainPage),
 ('/Success', Success)
], debug=True)