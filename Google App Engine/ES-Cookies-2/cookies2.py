import webapp2
import logging
import re
import cgi
import jinja2
import os
import hashlib

from google.appengine.ext import db

## see http://jinja.pocoo.org/docs/api/#autoescaping
def guess_autoescape(template_name):
   if template_name is None or '.' not in template_name:
      return False
      ext = template_name.rsplit('.', 1)[1]
      return ext in ('html', 'htm', 'xml')

def hash_str(s):
    return hashlib.md5(str(s)).hexdigest()

def make_secure_val(s):
    return str(s)+"|"+str(hash_str(s))

def check_secure_val(h):
    if make_secure_val(get_unhashed(h)) == h:
#    if hash_str(h) == make_secure_val(get_unhashed(h)):
        return get_unhashed(h)
    return None

def get_unhashed(s):
    return str(s).split('|', 1)[0]


JINJA_ENVIRONMENT = jinja2.Environment(
   autoescape=guess_autoescape,     ## see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Handler(webapp2.RequestHandler):
    def write(self, *items):    
        self.response.write(" : ".join(items))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):   

    def get(self):
        isGood = True;
        logging.info("********** MainPage GET **********")
        self.response.headers['Content-Type'] = 'text/plain'
        visits = self.request.cookies.get('visits','0') 
        ##1 Assign the variable 'visits' to the value of the 'visits' 
        ##1 cookie obtained from the browsers HTTP response. If the cookie 
        ##1 does not exist, set the variable 'visits' to '0'
        if(not visits.isdigit()):
            if(check_secure_val(visits) != None):
                visits = make_secure_val(int(get_unhashed(visits)) + 1)
#            visits = int(visits)+1
            else: 
                isGood = False;
                visits = make_secure_val(0)
        else:
            isGood = False;
            visits = make_secure_val(0)
        ##2 If the variable visits is an integer (i.e. use str.isdigit())
        ##2 increment visits by 1
        ##2 else set visits to 0

        self.response.headers.add_header('Set-Cookie', 'visits=%s' % visits)
        ##3 Add the 'Set-Cookie:' header with the value set to the 
        ##3 variable 'visits' to the HTTP response

        if(isGood):
            if(int(get_unhashed(visits)) >= 10000):
                self.response.write("Congratulations!")
            else:
                self.response.write('visits=%s' % get_unhashed(visits)) 
        else:
            self.response.write('Stop being sketchy')

###
###
### NEED TO UNHASH ONE MORE TIME SOMEWHERE
###
###


        ##4 if visits > 10000, 
        ##4   write out a congratulations message
        ##4 else
        ##4   write out a message stating how many times the user has visited

    def post(self):
        logging.info("DBG: MainPage POST")

application = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
