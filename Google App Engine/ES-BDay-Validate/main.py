import webapp2
import cgi

form = """
<p> What is your birthday? </p>
<form method="post" action="/">
<label> Month <input type="text" name="Month" value="%(month)s"> </label>
<label> Day   <input type="text" name="Day"   value="%(day)s">   </label>
<label> Year  <input type="text" name="Year"  value="%(year)s">  </label>
<div style="color: red">%(error)s</div>
<input type="submit">
</form>
"""

def escape_html(s):
    return cgi.escape(s, quote = True)

def write_form(self, month="", day="", year="", error=""):
  self.response.write(form % {"error": error, "month": month, "day": day, "year": year})

def is_day_good(day):
  if(day.isnumeric()):
    if(int(day) > 0) and (int(day) <= 31):
      return True
  return False

def is_month_good(month):
  m = month.lower()
  if((m=="january") or (m=="february") or (m=="march") or(m=="april") or (m=="may") or(m=="june") or(m=="july") or(m=="august") or (m=="september") or(m=="october") or(m=="november") or(m=="december")):
    return True
  return False

def is_year_good(year):
  if(year.isnumeric()):
    if((int(year) > 1900) and (int(year) <= 2016)):
      return True
  return False

class MainPage(webapp2.RequestHandler):

  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write("<h1>Welcome!</h1>")
    write_form(self)

  def post(self):
      d = self.request.get("Day")
      m = self.request.get("Month")
      y = self.request.get("Year")
      dg = is_day_good(d)
      mg = is_month_good(m)
      yg = is_year_good(y)

      if(dg and mg and yg):
        self.redirect('/Success')
      else:
        write_form(self, escape_html(m), escape_html(d), escape_html(y), "Wrong")

class Success(webapp2.RequestHandler):
  def get(self):
    self.response.write("<h`>Good Work!</h1>")


application = webapp2.WSGIApplication([
 ('/', MainPage),
 ('/Success', Success)
], debug=True)