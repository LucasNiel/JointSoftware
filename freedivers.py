import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

MAIN_PAGE_FOOTER_TEMPLATE = """\
        <form action="/sign?%s" method="post">
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Sign Guestbook"></div>
        </form>
        <hr>
        <form>Guestbook name:
            <input value="%s" name="guestbook_name">
            <input type="submit" value="switch">
        </form>
        <a href="%s">%s</a>
    </body>
</html>
"""

DEFAULT_GUESTBOOK_NAME = "default_guestbook"

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    #Constructs a Datastore key for a Guestbook entity.
    #We use guestbook_name as the key.

    return ndb.Key('Guestbook',guestbook_name)


class DiverUser(ndb.Model):
	#stores info about users
	userId = ndb.StringProperty(indexed=False)
	fruit = ndb.StringProperty(indexed=False)

class Author(ndb.Model):
    #Sub model for representating an author.
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Greeting(ndb.Model):
    #A main model for representing an individual Guestbook entry
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
		
		#myVar = 23
	
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user':user,
            'greetings':greetings,
            'guestbook_name':urllib.quote_plus(guestbook_name),
            'url':url,
            'url_linktext':url_linktext
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
	


class Events(webapp2.RequestHandler):

	def get(self):
		self.response.write("EVENTS")
		
		
	
class UserCreate(webapp2.RequestHandler):

	def post(self):
		#capture the form data and save to db
		user_id = "blank"
		user = users.get_current_user()
		if user:
			userId = user.user_id()
		else:
			self.redirect(users.create_login_url(self.request.uri))
		
		#guestbook_name = DEFAULT_GUESTBOOK_NAME
		#newUser = DiverUser(parent=guestbook_key(guestbook_name))
		
		
		#newUser.fruit ="Apple"
        #newUser.put()

class Users(webapp2.RequestHandler):

	def get(self):
		name = self.request.get('name')
		reps = int(self.request.get('reps'))
		
		user = users.get_current_user()
		
		if user:
			name = user.nickname()
		else:
			self.redirect(users.create_login_url(self.request.uri))
		
		template_values = {
			'name':name,
			'reps':reps
		}
		template = JINJA_ENVIRONMENT.get_template('users.html')
		self.response.write(template.render(template_values))
		

class Guestbook(webapp2.RequestHandler):

    def post(self):
        #We set the same parent key on the 'Greeting' to ensure each
        #Greeting is in the same parent entity group. Queries across the
        #single entity group will be consistent. However, the write
        #rate to a single entity group should be limited to
        # ~1/second.

        guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))
		
        if users.get_current_user():
            greeting.author = Author(
				identity=users.get_current_user().user_id(),
                email=users.get_current_user().email())
            greeting.content = self.request.get('content')
            greeting.put()

            query_params = {'guestbook_name': guestbook_name}
            self.redirect('/?' + urllib.urlencode(query_params))

app = webapp2.WSGIApplication([
        ('/',MainPage),
        ('/events',Events),
		('/users',Users),
		('/userCreate',Guestbook)
], debug = True)
