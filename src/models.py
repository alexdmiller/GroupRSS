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

# TODO: create a group
class Group(db.Model):
  name = db.StringProperty()
  description = db.StringProperty()

  def getFeeds(self):
    return GroupFeed.gql('WHERE group = :1', self.key())

class GroupFeed(db.Model):
  group = db.ReferenceProperty(Group, collection_name='group_feeds')
  feed = db.ReferenceProperty(Feed, collection_name='feed_groups')

# figure out when to create and save group post models (probably when group feed
# is requested? or when post is created?)
class GroupPost(db.Model):
  group = db.ReferenceProperty(Group, collection_name='group_posts')
  post = db.ReferenceProperty(Post, collection_name='post_groups')
