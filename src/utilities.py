# coding: utf-8
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import db
import simplejson as json
import database
import facebook
import urllib
import logging

# Information of facebook api key.
facebook_API_KEY = '434c87a5cf8faac117f53eccc9a3e335'
facebook_APP_ID = '142892519093949'
facebook_APP_SECRET= '963cf12901646fff05b64248712186b2'

class tmBundle(dict):
    """ Bundle to render template with custom data. """
    def __init__(self, title=None, error=None):
        self["APIKEY"] = facebook_API_KEY
        self["APPID"]  = facebook_APP_ID
        
        if title:
            self['title'] = title
        if error:
            self['error'] = error
    def addProperty(self, name, content):
        self[name] = content

def doRender(self, name, bundle):
    """ Auto choose template to render"""
    name = name + '.html'
    tm_path = '/'.join(['templates',name])
    self.response.out.write(template.render(tm_path, bundle, debug=True))
    # remove debug flag after release application.
    
def debugStatus():
    return True

def validateSchoolPOPServer(username, password):
    form_fields = {'USERID': username,
                   'PASSWD': password}
    
    form_data = urllib.urlencode(form_fields)
    
    targetURL = "http://nccu.edu.tw/cgi-bin/login"
    
    try:
        result = urlfetch.fetch(url = targetURL,
                                payload = form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                follow_redirects=False)
    except:
        logging.error("School mail server not response.")
        result = urlfetch.fetch(url = targetURL,
                                payload = form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                follow_redirects=False)
    finally:
        if result.content.split("\"")[3][1:4] == "cgi":
            return True
        else:
            return False
    
def getCurrentFacebookID(self):
    facebookUser = facebook.get_user_from_cookie(self.request.cookies, facebook_APP_ID, facebook_APP_SECRET)
    logging.info(str(facebookUser))
    if facebookUser:
        graph = facebook.GraphAPI(facebookUser["access_token"])
        fid = facebookUser["uid"]
        logging.info("graph.get_object('fid') -> " + fid)
        if fid:
            logging.info("get fid = %s"%fid)
            return fid
        else:
            logging.error("fid is empty.")
        
def getDepartOptions():
    """function to generate html options code."""
    data = json.loads(open("departlist.json").read())
    html = ""
    for college in data.keys():
        for depart in data[college].keys():
            if depart == 'name':
                continue
            html += '<option value="%s">%s</option>\n'%(college+depart, data[college][depart])
    
    
    return html
            
            
def getFidsWithDepartments():
    bundleToReturn = []
    data = json.loads(open("departlist.json").read())
    for college in data.keys():
        for depart in data[college].keys():
            if depart == 'name':
                continue
            temp = []
            depart_id = college+depart
            
            query = database.members.gql("WHERE depart_id = :depart_id", depart_id = depart_id)
            results = query.fetch(10)
            temp = [result.fid for result in results]
            temp.insert(0, depart_id)
            temp.insert(0, data[college][depart].encode('utf-8'))
            bundleToReturn.append(temp)
            
    return bundleToReturn
            
    
