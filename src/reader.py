import feedparser
from time import mktime
from datetime import datetime
from models import *

class Reader:
  def __init__(self, feedModel):
    self.feedModel = feedModel
    self.parsedFeed = None

  def fetchFeed(self):
    if self.parsedFeed is None:
      self.parsedFeed = feedparser.parse(self.feedModel.url)

  def saveMetadata(self):
    self.fetchFeed()
    self.feedModel.name = self.parsedFeed.channel.title
    self.feedModel.put()

  def savePosts(self):
    self.fetchFeed()
    updated_parsed_datetime = None
    if self.parsedFeed.feed.updated_parsed:
      updated_parsed_datetime = datetime.fromtimestamp(
          mktime(self.parsedFeed.feed.updated_parsed))
    # TODO: test that this loop doesn't happen if last_checked < updated
    # TODO: ask server for last updated before we request all of the posts?
    # TODO: only update last_updated on success
    if (self.feedModel.last_checked is None) or (self.feedModel.last_checked < updated_parsed_datetime):
      for entry in self.parsedFeed.entries:
        post = Post.get_by_key_name(entry.link)
        if post is None:
          timestamp = datetime.fromtimestamp(mktime(entry.published_parsed))
          print timestamp
          post = Post(key_name = entry.link,
                      feed = self.feedModel,
                      url = entry.link,
                      title = entry.title,
                      timestamp=timestamp)
          post.put()
          self.createGroupPost(post, self.feedModel);

      self.feedModel.last_checked = updated_parsed_datetime
      self.feedModel.put()

  def createGroupPost(self, post, feed):
    for feed_group in feed.feed_groups:
      GroupPost(group=feed_group.group, post=post).put()