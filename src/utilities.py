# coding: utf-8
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson as json
import database
import facebook
import urllib
import logging
import random

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
            self['title'] = "發生錯誤"
            self['error'] = error
    def addProperty(self, name, content):
        self[name] = content

def doRender(self, name, bundle):
    """ Auto choose template to render"""
    if bundle.has_key("error"):
        name = 'error'
        bundle.addProperty("title", "發生錯誤")
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
    targetURL2 = "http://faculty.nccu.edu.tw/cgi-bin/login"
    
    try:
        result = urlfetch.fetch(url = targetURL,
                                payload = form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                follow_redirects=False)
    except:
        logging.error("School mail server not response.")
        result = urlfetch.fetch(url = targetURL2,
                                payload = form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                follow_redirects=False)
    finally:
        if "function redirect()" in result.content:
            return True
        else:
            return False
    
def getCurrentFacebookID(self):
    facebookUser = facebook.get_user_from_cookie(self.request.cookies, facebook_APP_ID, facebook_APP_SECRET)
    logging.info("Fid from cookie: "+str(facebookUser))
    if facebookUser:
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
        html+= '<option disabled>----------'+data[college]['name']+'----------</option>\n'
        for depart in data[college].keys():
            if depart == 'name':    
                continue
            html += '<option value="%s">%s</option>\n'%(college+depart, data[college][depart])
    
    
    return html
            
            
def getFidsWithDepartments():
    bundleToReturn = memcache.get('FidsWithDeparts')
    if bundleToReturn:
        logging.info("Fids and departs information exists in memcache, reuse it.")
        return bundleToReturn
    logging.info("Fids and departs disappear from memcache, rebuild it.")
    bundleToReturn = []
    data = json.loads(open("departlist.json").read())
    for college in data.keys():
        for depart in data[college].keys():
            if depart == 'name':
                continue
            temp = []
            depart_id = college+depart
            
            query = database.members.gql("WHERE depart_id = :depart_id", depart_id = depart_id)
            results = query.fetch(1000)
            temp = [result.fid for result in results]
            length = len(temp)
            if length>14:
                temp = random.sample(temp, 14)
            else:
                temp = random.sample(temp, length)

            temp.insert(0, str(length))
            temp.insert(0, depart_id)
            temp.insert(0, data[college][depart].encode('utf-8'))
            bundleToReturn.append(temp)
    
    bundleToReturn.sort(key=lambda x:int(x[2]) , reverse=True)
    memcache.add("FidsWithDeparts", value=bundleToReturn, time=3600)
    return bundleToReturn

def getMembersByDepartId(depart_id, tors):

    cache_id = "depart_" + depart_id + "_" + str(tors)
    bundleToReturn = memcache.get(cache_id)
    if bundleToReturn:
        return bundleToReturn
    
    query = database.members.gql("WHERE depart_id = :depart_id AND tors = :tors", depart_id = depart_id, tors = tors)
    results = query.fetch(1000)
    temp = [result.fid for result in results]
    logging.info(temp)
    memcache.add(cache_id, value=temp, time=7200)
    return temp
    
    

def getDepartNameById(depart_id):
    prefix_depart_id = depart_id[0:2]
    postfix_depart_id = depart_id[2:4]
    depart_list = json.loads(open("departlist.json").read())
    try:
        depart_name = depart_list[prefix_depart_id][postfix_depart_id]
    except KeyError:
        return None
    else:
        return depart_name
    