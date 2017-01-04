import webapp2
import logging
import re
import cgi
import jinja2
import os
import hmac
import time

from google.appengine.ext import db


# Color names aranged by value (index=value)
COLORS = [
    'black',
    'brown',
    'red',
    'orange',
    'yellow',
    'green',
    'blue',
    'violet',
    'grey',
    'white']

# Multipliers in a dictionary, organized by value for ease of reading
MULTIPLIER = {
    1e0:    'black',
    1e1:    'brown',
    1e2:    'red',
    1e3:    'orange',
    1e4:    'yellow',
    1e5:    'green',
    1e6:    'blue',
    1e7:    'violet'}


# RGB Color Codes
COLORCODES = {
    "black":    "#000000",
    "brown":    "#a52a2a",
    "red":      "#ff0000",
    "orange":   "#ffa500",
    "yellow":   "#ffff00",
    "green":    "#008000",
    "blue":     "#0000ff",
    "violet":   "#800080",
    "grey":     "#808080",
    "white":    "#ffffff",
    "silver":   "#c0c0c0",
    "gold":     "#d4a017"}

class ResistorObject(db.Model):
    added_by = db.StringProperty()
    colors = db.StringProperty()
    amount_of_resistors = db.StringProperty()
    ohm_value_as_string = db.StringProperty()
def getColors(num):
    # To-be return value
    returnVals = []
    failReturnVals = [COLORS[0], COLORS[0], MULTIPLIER[1e0]]
    # Process the number
    indexPlaceholder = 0
    numStr = str(num)
    bandValues = ""
    indexPlaceholder = 2
    bandValues = numStr[:indexPlaceholder]
    # If there's 4 stripes
    if (num / float(bandValues)) % 10:
        indexPlaceholder = 3
        bandValues = numStr[:indexPlaceholder]
    # If there's a third band to add
    if len(numStr) > indexPlaceholder:
        if numStr[indexPlaceholder] != "0":
            bandValues = numStr[:indexPlaceholder + 1]
    # Needs another black band
    if len(bandValues) < 2:
        bandValues = bandValues + "0"
    for value in bandValues:
        if value == ".":
            continue
        returnVals.append(COLORS[int(value)])
    returnVals.append(MULTIPLIER[round(num / float(bandValues.replace(".", "")), 2)])
    return returnVals
def isvalid(input):
    return(len(input.split(" ")) == 2)

#List of colors (strings) to ohms (float)
def getOhms(colors):
    bandValues = ""
    multiply = 0
    # Get the index numbers of the colors
    while len(colors) > 1:
        bandValues = bandValues + str(COLORS.index(colors.pop(0)))
    # Find the key (multiplier) based on color (no easy way to do this)
    for key, value in MULTIPLIER.items():
        if value == colors[0]:
            multiply = key
            break
    # Color value * multiplier
    return float(bandValues) * multiply

## see http://jinja.pocoo.org/docs/api/#autoescaping
def guess_autoescape(template_name):
   if template_name is None or '.' not in template_name:
      return False
      ext = template_name.rsplit('.', 1)[1]
      return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
   autoescape=guess_autoescape,     ## see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Handler(webapp2.RequestHandler):
    ## saves you from having to type self.response.out.write
    def write(self, a):            
        self.response.out.write(a)
    
    ## takes a template and dictionary and returns a string with the rendered template
    def render_str(self, template, **params): 
	template = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return template.render(params)

    ## takes a template and dictionary and writes the rendered template
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

SECRET="imsosecret"
def hash_str(s):
   return hmac.new(SECRET,s).hexdigest()

def make_secure_val(s):
   return s+'|'+hash_str(s)

def check_secure_val(h):
   val = h.split('|')[0]
   if (h == make_secure_val(val)):
      return True
   return False

class MainPage(Handler):   
    def get(self):
        userId = self.request.cookies.get('user_id', 'bad')

        if(check_secure_val(userId)):
            self.redirect('/resistors')
        title1 = "Web Applications Midterm"
        title2 = "Good Luck"
        title3 = "Enter your name"
        title4 = ""
        self.render("front.html",
        place_holder1=title1,
        place_holder2=title2,
        place_holder3=title3,
        place_holder4=title4)

    def post(self):
        input = self.request.get("name")
        if(isvalid(input)):
            nameVal = input.split(" ")[0] + "+" + input.split(" ")[1]
            idVal = nameVal + "|" + hash_str(nameVal)
            self.response.headers.add_header('Set-Cookie', 'user_id=%s' % str(idVal))
            self.redirect('/resistors')
            return
        else:
            self.response.headers.add_header('Set-Cookie', 'user_id=broke')
            title1 = "Web Applications Midterm"
            title2 = "Good Luck"
            title3 = "Enter your name"
            title4 = "Make sure you have a first and last name"
            self.render("front.html",
            place_holder1=title1,
            place_holder2=title2,
            place_holder3=title3,
            place_holder4=title4)
class Resistors(Handler):
    def get(self):
        self.render("resistors.html", 
                    resistance_value='',
                    show_image=False)
    def post(self):
        colorstoinput = [self.request.get("s1"), self.request.get("s2"), self.request.get("s3"), self.request.get("s4")]
        ohmValue = str(getOhms(colorstoinput))
        numofzeroes = 0
        for i in ohmValue:
            if i == '0':
                numofzeroes += 1
        numofzeroes -= 1
        if numofzeroes >= 6:
            ohmValue = ohmValue[:-8] + "M"
        elif numofzeroes >= 3:
            ohmValue = ohmValue[:-5] + "K"

        if self.request.get("amount") != '':
            if check_secure_val(self.request.cookies.get('user_id', '')):
                temp_resistor = ResistorObject()
                temp_resistor.ohm_value_as_string = ohmValue
                temp_resistor.colors = self.request.get("s1") + " " + self.request.get("s2") + " " + self.request.get("s3") + " " + self.request.get("s4")
                temp_resistor.amount_of_resistors = self.request.get("amount")
                users_name = self.request.cookies.get('user_id', 'unknown')
                users_name = users_name.split("|", 2)[0]
                users_name = users_name.split("+", 2)[0] + " " + users_name.split("+", 2)[1]

                temp_resistor.added_by = users_name

                temp_resistor.put()
                time.sleep(.2)
            else:
                self.redirect('/')
                return
        self.render("resistors.html",
                        resistance_value=ohmValue,
                        show_image=True,
                        s1_val = self.request.get("s1"),
                        s2_val = self.request.get("s2"),
                        s3_val = self.request.get("s3"),
                        s4_val = self.request.get("s4"))

class ShowDatabase(Handler):
    def get(self):
        values_to_show = db.GqlQuery("SELECT * FROM ResistorObject ORDER BY ohm_value_as_string")
        self.render("databasepage.html",
                values = values_to_show)


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/resistors', Resistors),
    ('/resistors/', Resistors),
    ('/resistors/database', ShowDatabase),
    ('/resistors/database/', ShowDatabase),
], debug=True)
