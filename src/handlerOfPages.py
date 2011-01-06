# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from utilities import *

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        bundle = tmBundle(title="FaceMap@NCCU - 政大人的Facebook通訊錄")
        doRender(self, 'index', bundle)
        

class RegisterPage(webapp.RequestHandler):
    def get(self):
        bundle = tmBundle(title = '註冊 - 使用者和站方協議')
        bundle.addProperty("license", open("license.txt").read())
        doRender(self, 'register_welcome', bundle)
    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        action = self.request.get('action')
        
        if action == 'agree':
            bundle = tmBundle(title = '註冊 - 驗證您的學校帳號')
            doRender(self, 'register', bundle)
        elif action == 'validated':
            school_account = self.request.get('username')
            school_password = self.request.get('password')
            result = validateSchoolPOPServer(school_account, school_password)
            
            bundle = tmBundle(title = "註冊 - 整合您的Facebook帳號")
            bundle.addProperty("schoolChecked", result)
            bundle.addProperty("schoolAccount", school_account)
            bundle.addProperty("departOptions", getDepartOptions())
            
            doRender(self, 'register_form', bundle)
        elif action == 'finish':
            fid = getCurrentFacebookID(self)
            schoolid = self.request.get('form_school_id')
            tors = self.request.get('form_ident')
            depart_id = self.request.get("form_depart")
            bundle = tmBundle(title = "註冊 - 完成")
            bundle.addProperty("schoolAccount", schoolid)
            
            query = database.members.gql("WHERE school_id = :schoolid", schoolid=schoolid)
            results = query.fetch(limit = 1)
             
            if len(results) == 0:
                if fid:
                    memberToStore = database.members(school_id=schoolid,
                                                     fid = fid,
                                                     tors = int(tors),
                                                     depart_id = depart_id)
                    try:
                        memberToStore.put()
                    except:
                        logging.error("Error occur at storing the data of student: %s", schoolid)
                        bundle.addProperty("error", "連線到Facebook.com的過程中發生錯誤，請稍後重新再試。")
                    else:
                        memcache.delete("FidsWithDeparts")
                        memcache.delete("depart_"+depart_id+"_"+str(tors))
                        logging.info("Memcache flushed because of new register.")
                        logging.info("School id: %s just register with fid: %s"%(schoolid, fid))
                        
    
                else:
                    bundle.addProperty('error', "連線到Facebook時發生錯誤，請稍後再試。")
                    

            else:
                logging.error("School id '%s' has been registed, blocked."%schoolid)
                bundle.addProperty("error", "你的學校帳號已經被註冊過了，請聯絡系統管理員。")
            
            doRender(self, "register_finish", bundle)
            
                
class WallPage(webapp.RequestHandler):
    def get(self):
        
        action = self.request.get('action')
        
        if action == "depart_detail":
            depart_id = self.request.get("depart_id")
            if len(depart_id) != 4:
                bundle=tmBundle(error='系所ID不存在。')
                doRender(self, 'error', bundle)
            bundle = tmBundle(title="系所目錄 - %s"%getDepartNameById(depart_id).encode('utf-8'))
            students = getMembersByDepartId(depart_id, 1)
            teachers = getMembersByDepartId(depart_id, 0)
            bundle.addProperty("students", students)
            bundle.addProperty("teachers", teachers)
            
            
            doRender(self, 'wall_detail', bundle)
        else:
            bundle = tmBundle(title="系所目錄")
            bundle.addProperty('list', getFidsWithDepartments())
            doRender(self, 'wall', bundle)
        
class ChatroomPage(webapp.RequestHandler):
    def get(self):
        bundle = tmBundle(title="政大塗鴉牆")
        
        
        doRender(self, 'chatroom_test', bundle)
        
class AboutPage(webapp.RequestHandler):
    def get(self):
        bundle = tmBundle(title="關於Facemap@NCCU")
        doRender(self, 'about', bundle)

sitemap = [('/pages/', MainPage),
           ('/pages/register', RegisterPage),
           ('/pages/wall', WallPage),
           ('/pages/chatroom', ChatroomPage),
           ('/pages/about',AboutPage)]

application = webapp.WSGIApplication(sitemap , debug=debugStatus())


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
