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
        
        if result:
            self.response.out.write(json.dumps(result))
        else:
            self.response.out.write(json.dumps(result))
            
class RedirectToFacebookByFIDHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8';
        bundle = tmBundle(title = "轉址中")
        fid = self.request.get('fid')
        #result = urlfetch.fetch(url = 'https://graph.facebook.com/'+fid)
        #graph = json.loads(result.content)
        try:
            self.redirect("http://www.facebook.com/profile.php?id="+fid)
        except:
            bundle.addProperty("error", "頁面遺失。")
            doRender(self, 'error', bundle)
            
        """    
        if 1:
            graph = facebook.GraphAPI()
            profile = graph.get_object(fid)
            try:
                self.redirect(profile['link'])
            except KeyError,e:
                logging.info("fid: %s's link doesn't exist. Error code: %s"%(fid,e))
                bundle.addProperty('error', str(e))
                doRender(self, 'error', bundle)
        else:
            bundle.addProperty('title', '發生錯誤')
            bundle.addProperty('error', "Facebook ID發生錯誤，請用正常方式使用本站。")
            doRender(self, "error", bundle)
        """   
        
        
class CheckUserHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8';
        fid = self.request.get("user")
        result = database.members.gql("WHERE fid = :fid", fid = fid).fetch(1)
        if result:
            self.response.out.write("1")
        else:
            self.response.out.write("0")
        
class GetProfileByFidHandler(webapp.RequestHandler):
    def get(self):
        jsonBundle = getProfileJSONBundle(self)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(json.dumps(jsonBundle))
        
class GetProfileByAccessTokenHandler(webapp.RequestHandler):
    def get(self):
        jsonBundle = getProfileJSONBundle2(self)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(json.dumps(jsonBundle))
        
class GetStudentsByDepartIdHandler(webapp.RequestHandler):
    def get(self):
        departid = self.request.get('departid')
        students_results = database.members.gql("WHERE depart_id = :depart_id", depart_id = departid).fetch(1000)
        students = [result.fid for result in students_results if result.tors == 1]
        teachers = [result.fid for result in students_results if result.tors == 0]
        jsonBundle = {'depart_id': departid, 'students':students, 'teachers': teachers}
        self.response.headers["Content-Type"] = 'text/plain'
        self.response.out.write(json.dumps(jsonBundle))
        
        
        

sitemap = [('/apis/validateSchool', ValidateSchoolAccountHandler ),
           ('/apis/rediecttofbbyfid', RedirectToFacebookByFIDHandler),
           ('/apis/checkuser',CheckUserHandler),
           ('/apis/getprofilebycookie', GetProfileByFidHandler),
           ('/apis/getprofilebyaccesstoken', GetProfileByAccessTokenHandler),
           ('/apis/getstudentsbydepartid', GetStudentsByDepartIdHandler)]

application = webapp.WSGIApplication(sitemap, debug=debugStatus())

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()