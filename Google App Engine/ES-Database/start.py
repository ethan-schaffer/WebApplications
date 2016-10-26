import webapp2
import logging
import re
import jinja2
import os
from google.appengine.ext import db

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

class Art(db.Model):
    title = db.StringProperty()
    body = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)


class MyHandler(webapp2.RequestHandler):
    def write(self, *writeArgs):    
        self.response.write(" : ".join(writeArgs))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
    def get(self):
        pictures = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        dictionary = {"pictures": pictures, "message": ""}
        template = JINJA_ENVIRONMENT.get_template('/templates/index.html')
        self.response.write(template.render(dictionary))

    def post(self):
        artInst = Art()
        artInst.title = self.request.get("text")
        artInst.body = self.request.get("art")
        if(not artInst.body) and (not artInst.title):
            artInst.put()
            message = "Fill in both Boxes"
        else:
            message = "Thanks!"
        pictures = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        dictionary = {"arts": pictures, 
                    "message": message}
        template = JINJA_ENVIRONMENT.get_template('/templates/index.html')
        self.response.write(template.render(dictionary))

application = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
