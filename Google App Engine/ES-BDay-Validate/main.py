import webapp2

form = """
<p> What is your birthday? </p>
<form method="post" action="/Validater">
<label for="Day">Day</label>
<input name="Day">
<label for="Month">Month</label>
<input name="Month">
<label for="Year">Year</label>
<input name="Year">
<div style="color: red">%(error)s</div>
<input type="submit">
</form>
"""

def write_form(self, error=""):
  self.response.write(form % {"error": error})

def is_day_good(day):
  if(day.isnumeric()):
    if((int(day) > 0) and (int(day)<=31)):
      return True
  return False

def is_month_good(month):
  m = month.lower()
  if((m=="january") or (m=="february") or (m=="march") or(m=="april") or (m=="may") or(m=="june") or(m=="july") or(m=="august") or (m=="september") or(m=="october") or(m=="november") or(m=="december")):
    return True
  return False

def is_year_good(year):
  if(year.isnumeric()):
    return True
    if((year>1900) and (year<=2016)):
      return True
  return False

class MainPage(webapp2.RequestHandler):

  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write("<h1>Welcome!</h1>")
    write_form(self)

class Validater(webapp2.RequestHandler):

  def post(self):
      d = self.request.get("Day")
      m = self.request.get("Month")
      y = self.request.get("Year")
      dg = is_day_good(d)
      mg = is_month_good(m)
      yg = is_year_good(y)

      if(dg and mg and yg):
        self.response.write("Thanks!")
      else:
        write_form(self, "Wrong")



application = webapp2.WSGIApplication([
 ('/', MainPage),
 ('/Validater', Validater)
], debug=True)