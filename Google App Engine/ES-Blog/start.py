import webapp2
import logging
import re
import jinja2
import os
import time
from google.appengine.ext import db
# TImes:   '%A %B %d %Y'     '%H %M %S'

global error
error = False
def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

## see http://jinja.pocoo.org/docs/api/#autoescaping
JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=guess_autoescape,     ## see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class MyHandler(webapp2.RequestHandler):
    def write(self, *writeArgs):    
        self.response.write(" : ".join(writeArgs))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    subject = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class BlogHome(MyHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC limit 10")
        dictionary = {"posts": posts, 
                    "Title": "Ethan's Blog!"}
        self.render('posts.html', **dictionary)

    def post(self):
        self.redirect('/blog/')

class WriteABlogPost(MyHandler):
    def get(self):
        global error
        errorMessage = ("Uh oh, that's not quite right" if error else "")
        dictionary = {"ph_subject": "Your Subject Here", "ph_content": "Your Post Here", "ph_error": errorMessage}
        self.render('newpost.html', **dictionary)

    def post(self):
        temp = BlogPost()
        temp.subject = self.request.get("subject")
        temp.content = self.request.get("content")
        time.sleep(.2)
        if (temp.subject) and (temp.content):
            temp.put()
            time.sleep(.2)
            error = False
            logging.info("**** L O G ******")
            self.redirect('/blog/%s'%str(temp.key().id()))
        else:
            error = True
            self.redirect('/blog/register')

class ReDir(MyHandler):
    def get(self):
        self.redirect('/blog/newpost')

class SinglePost(MyHandler):
    def get(self, blogid):
        logging.info("*************** SinglePost.get ****************")
        post = BlogPost.get_by_id(int(blogid))
        dictionary = {"post": post, 
                    "Title": "Ethan's new blog"}
        self.render('post.html', **dictionary)

    def post(self, blogid):
        logging.info("*************** SinglePost.get ****************")
        post = BlogPost.get_by_id(int(blogid))
        dictionary = {"post": post, 
                    "Title": "Ethan's new blog"}
        self.render('post.html', **dictionary)

application = webapp2.WSGIApplication([
    ('/', BlogHome),
    ('/newpost', ReDir),
    (r'/blog\/{0,1}', BlogHome),
    (r'/blog/(\d+)', SinglePost),
    (r'/blog/newpost\/{0,1}', WriteABlogPost),

], debug=True)
