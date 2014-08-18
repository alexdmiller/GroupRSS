from google.appengine.ext import db

class Feed(db.Model):
  url = db.StringProperty()
  name = db.StringProperty()
  last_checked = db.DateTimeProperty()

class Post(db.Model):
  feed = db.ReferenceProperty(Feed, collection_name='posts')  
  link = db.StringProperty()
  title = db.StringProperty()
  content = db.StringProperty()

class Group(db.Model):
  name = db.StringProperty()
  description = db.StringProperty()

class GroupPost(db.Model):
  owner_group_id = db.StringProperty()
  post_id = db.StringProperty()
