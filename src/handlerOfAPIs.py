# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json

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
            
class RedirectToFacebookByFIDHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8';
        fid = self.request.get('fid')
        result = urlfetch.fetch(url = 'http://graph.facebook.com/'+fid)
        graph = json.loads(result.content)
        bundle = tmBundle(title = "轉址中")
        try:
            self.redirect(graph['link'])
        except KeyError,e:
            logging.info("fid: %s's link doesn't exist. Error code: %s"%(fid,e))
            bundle.addProperty('title', '發生錯誤')
            doRender(self, 'error', bundle)
        
        
            
        

sitemap = [('/apis/validateSchool', ValidateSchoolAccountHandler ),
           ('/apis/rediecttofbbyfid', RedirectToFacebookByFIDHandler)]

application = webapp.WSGIApplication(sitemap, debug=debugStatus())

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()