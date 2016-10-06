import webapp2
import random

form = """
<p> Guess! </p>
<form method="post" action="/guesser">
<input name="guess">
<input type="submit">
</form>
"""

def rand_gen():
  global rnd
  rnd = random.randrange(1, 100)

global rnd
rnd = 0
rand_gen()

class MainPage(webapp2.RequestHandler):
  def get(self):
      rand_gen()
      self.response.headers['Content-Type'] = 'text/html'
      self.response.write("<h1>E</h1>")
      self.response.write(form)

class GuessHandler(webapp2.RequestHandler):
  def post(self):
      global rnd
      g = self.request.get("guess")
      self.response.write("You Guessed: " + str(g) + "<br>")
      self.response.write("Correct Number is: " + str(rnd) + "<br>")

      if(g.isnumeric()):
        if( int(g) == rnd):
          self.response.write("You're right! Good job guessing " + str(rnd))
        elif(int(g) < rnd):
          self.response.write("Your guess was too small!")
          self.response.write(form)
        else:
          self.response.write("Your guess was too big!")
          self.response.write(form)
      else:
          self.response.write("Not a number! Try again!")
          self.response.write(form)

application = webapp2.WSGIApplication([
 ('/', MainPage),
 ('/guesser', GuessHandler)
], debug=True)