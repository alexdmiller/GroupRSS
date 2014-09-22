import feedparser
from time import mktime
from datetime import datetime
from datetime import timedelta
from models import *
import logging
import httplib, urllib2, urlparse

class Reader:
  MIN_UPADTE_INTERVAL_MINUTES = 10

  def __init__(self, feedModel):
    self.feedModel = feedModel
    self.parsedFeed = None

  def fetchFeed(self):
    if self.feedModel.last_checked and (datetime.now() - self.feedModel.last_checked) < timedelta(minutes = Reader.MIN_UPADTE_INTERVAL_MINUTES):
      logging.info("Did not fetch feed %s because it was checked in the last %s minutes.", self.feedModel.url, Reader.MIN_UPADTE_INTERVAL_MINUTES)
      return
    if self.parsedFeed is None:
      if self.feedModel.last_checked:
        parsed = feedparser.parse(self.feedModel.url, etag=self.feedModel.last_etag,
            modified=self.feedModel.last_checked)
        if parsed.status is 200:
          self.parsedFeed = parsed
        else:
          logging.info("Feed %s did not return status 200 when requested; not updating.", self.feedModel.url)
      else:
        logging.info("Fetching feed %s", self.feedModel.url)
        self.parsedFeed = feedparser.parse(self.feedModel.url)

  def saveMetadata(self):
    self.fetchFeed()
    self.feedModel.name = self.parsedFeed.feed.title
    self.feedModel.site_url = self.parsedFeed.feed.link
    self.feedModel.put()

  def savePosts(self):
    self.fetchFeed()
    if self.parsedFeed:
      updated_parsed_datetime = None
      if self.parsedFeed.feed.updated_parsed:
        updated_parsed_datetime = datetime.fromtimestamp(
            mktime(self.parsedFeed.feed.updated_parsed))
      # TODO: test that this loop doesn't happen if last_checked < updated
      # TODO: ask server for last updated before we request all of the posts?
      # TODO: only update last_updated on success
      if (self.feedModel.last_checked is None) or (self.feedModel.last_checked < updated_parsed_datetime):
        post_count = 0
        for entry in self.parsedFeed.entries:
          post = Post.get_by_key_name(entry.link)
          if post is None:
            timestamp = datetime.fromtimestamp(mktime(entry.published_parsed))
            post = Post(key_name=entry.link,
                        feed=self.feedModel,
                        url=entry.link,
                        title=entry.title,
                        summary=entry.summary,
                        timestamp=timestamp)
            post.put()
            post_count += 1
            self.createGroupPost(post, self.feedModel);
        logging.info("Added %s posts to feed %s", post_count, self.feedModel.url)
      self.feedModel.last_checked = datetime.now()
      if hasattr(self.parsedFeed, 'etag'):
        self.feedModel.last_etag = self.parsedFeed.etag
      self.feedModel.put()

  def createGroupPost(self, post, feed):
    for feed_group in feed.feed_groups:
      GroupPost.from_post(group=feed_group.group, post=post).put()