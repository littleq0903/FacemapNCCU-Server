# coding: utf-8
from google.appengine.ext import db
    
class members(db.Model):
    """tors means whether the member is a student or teacher, 0 means student and 1 means teacher.
    school_id: school account (ex. 98703060)
    fid: facebook id 
    tors: teacher or student,(0->teacher, 1->student)
    depart_id: id to present the department students belong to
    """
    school_id = db.StringProperty(required=True)
    fid = db.StringProperty(required=True)
    tors = db.IntegerProperty(required=True)
    depart_id = db.StringProperty(required=True)
    register_time = db.DateTimeProperty(required=True, auto_now_add=True)
    
    