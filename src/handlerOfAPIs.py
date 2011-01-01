# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import simplejson as json

from utilities import *

class ValidateSchoolAccountHandler(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        username_post = self.request.get('username')
        password_post = self.request.get('password')
        result = validateSchoolPOPServer(username_post, password_post)
        jsonBundle={'result':result}
        
        if result:
            self.response.out.write(json.dumps(result))
        else:
            self.response.out.write(json.dumps(result))
            
        

sitemap = [('/apis/validateSchool', ValidateSchoolAccountHandler )]

application = webapp.WSGIApplication(sitemap, debug=debugStatus())

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()