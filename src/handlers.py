# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from utilities import *
import logging

class EntranceHandler(webapp.RequestHandler):
    def get(self):
        self.redirect("/pages/")
        
        
sitemap = [("/.*", EntranceHandler)]

app = webapp.WSGIApplication(sitemap, debug = debugStatus())

def main():
    run_wsgi_app(app)
    
if __name__ == "__main__":
    main()
