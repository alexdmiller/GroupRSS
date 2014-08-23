from google.appengine.ext import db

class Feed(db.Model):
  url = db.StringProperty()
  name = db.StringProperty()
  last_checked = db.DateTimeProperty()

class Post(db.Model):
  feed = db.ReferenceProperty(Feed, collection_name='posts')  
  url = db.StringProperty()
  title = db.StringProperty()
  content = db.StringProperty()
  timestamp = db.DateTimeProperty()

class Group(db.Model):
  name = db.StringProperty()
  description = db.StringProperty()

class GroupFeed(db.Model):
  group = db.ReferenceProperty(Group, collection_name='group_feeds',
      required=True)
  feed = db.ReferenceProperty(Feed, collection_name='feed_groups',
      required=True)

class GroupPost(db.Model):
  group = db.ReferenceProperty(Group, collection_name='group_posts',
      required=True)
  post = db.ReferenceProperty(Post, collection_name='post_groups',
      required=True)
  timestamp = db.DateTimeProperty()

  @staticmethod
  def from_post(group, post):
    return GroupPost(group=group, post=post, timestamp=post.timestamp)
