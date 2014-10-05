from google.appengine.ext import db

class Feed(db.Model):
  # RSS url
  url = db.StringProperty()
  # Actual site url
  site_url = db.StringProperty()
  name = db.StringProperty()
  last_attempted_check = db.DateTimeProperty()
  last_attempted_check_status = db.DateTimeProperty()
  last_successful_check = db.DateTimeProperty()
  last_etag = db.StringProperty()

class Post(db.Model):
  feed = db.ReferenceProperty(Feed, collection_name='posts')  
  url = db.StringProperty()
  title = db.StringProperty()
  summary = db.TextProperty()
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
  last_modified = db.DateTimeProperty()

  def user_metadata(self, user):
    return UserPostMetadata.get_from_post(user, self)

  def comment_status_class(self, user):
    if self.comments.count() == 0:
      return 'no-comments'
    m = self.user_metadata(user)
    if m.last_read is None:
      return 'unread-comments'
    if m.last_read < self.last_modified:
      return 'unread-comments'
    else:
      return 'read-comments'

  @staticmethod
  def from_post(group, post):
    return GroupPost(group=group, post=post, timestamp=post.timestamp, last_modified=post.timestamp)

class GroupPostComment(db.Model):
  group_post = db.ReferenceProperty(GroupPost, collection_name='comments')
  content = db.TextProperty()
  user = db.UserProperty()
  timestamp = db.DateTimeProperty(auto_now_add=True)

class UserPostMetadata(db.Model):
  timestamp = db.DateTimeProperty()
  read = db.BooleanProperty()
  last_read = db.DateTimeProperty()

  @staticmethod
  def get_from_post(user, group_post):
    return UserPostMetadata.get_or_insert(str(user.user_id()) +
        str(group_post.key().id_or_name()))
