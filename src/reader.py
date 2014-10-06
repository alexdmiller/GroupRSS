import feedparser
from time import mktime
from datetime import datetime
from datetime import timedelta
from google.appengine.ext import db
from models import *
import logging
import httplib, urllib2, urlparse

class Reader:
  MIN_UPADTE_INTERVAL_MINUTES = 1

  @staticmethod
  def create(feed_model):
    return Reader(feed_model, feedparser.parse)

  def __init__(self, feed_model, parseFunction):
    self.feed_model = feed_model
    self.parsed_feed = None
    self.parse = parseFunction

  def feedRequestedRecently(self):
    return self.feed_model.last_successful_check and (datetime.now() - self.feed_model.last_successful_check) < timedelta(minutes = Reader.MIN_UPADTE_INTERVAL_MINUTES)

  def getFeed(self):
    # Already cached?
    if self.parsed_feed:
      return self.parsed_feed

    # Checking too often?
    if self.feedRequestedRecently():
      logging.info("Did not fetch feed %s because it was checked in the last %s minutes.", self.feed_model.url, Reader.MIN_UPADTE_INTERVAL_MINUTES)
      self.feed_model.set_status(Feed.OK, "Requesting feed too often.")
      self.feed_model.put()
      return None

    # Make HTTP request
    logging.info("Fetching feed %s", self.feed_model.url)
    parsed_feed = None
    if self.feed_model.last_successful_check:
      parsed_feed = self.parse(self.feed_model.url, etag=self.feed_model.last_etag,
          modified=self.feed_model.last_successful_check)
    else:
      parsed_feed = self.parse(self.feed_model.url)

    # Save feed status to model
    status = None
    status_level = None
    if hasattr(parsed_feed, 'status'):
      status = parsed_feed.status
      if status == 200 or status == 304:
        status_level = Feed.OK
      else:
        status_level = Feed.FATAL_ERROR
    elif parsed_feed.bozo is 1:
      status = parsed_feed.bozo_exception
      status_level = Feed.FATAL_ERROR

    self.feed_model.set_status(status_level, status)
    self.feed_model.put()

    logging.info("Feed %s returned status \'%s\'", self.feed_model.url, str(status))

    if status_level is Feed.OK:
      # Cache successful request
      self.parsed_feed = parsed_feed
      return parsed_feed

    # Don't cache or return anything for unsuccessful requests.
    return None

  #@db.transactional
  def saveMetadata(self, feed):
    self.feed_model.name = feed.feed.title
    self.feed_model.site_url = feed.feed.link
    self.feed_model.put()

  #@db.transactional
  def savePosts(self, feed):
    post_count = 0
    for entry in feed.entries:
      post = Post.get_by_key_name(entry.link)
      if post is None:
        timestamp = datetime.fromtimestamp(mktime(entry.published_parsed))
        post = Post(key_name=entry.link,
                    feed=self.feed_model,
                    url=entry.link,
                    title=entry.title,
                    summary=entry.summary,
                    timestamp=timestamp)
        post.put()
        post_count += 1
        self.createGroupPost(post, self.feed_model);
    logging.info("Added %s posts to feed %s", post_count, self.feed_model.url)

  def refresh(self):
    feed = self.getFeed()
    if feed:
      try:
        self.saveMetadata(feed)
        self.savePosts(feed)
      except Exception as exception:
        self.feed_model.last_attempted_check_status = str(exception)
      else:
        self.feed_model.last_successful_check = datetime.now()
        if hasattr(feed, 'etag'):
          self.feed_model.last_etag = feed.etag
        self.feed_model.put()

  def createGroupPost(self, post, feed):
    for feed_group in feed.feed_groups:
      GroupPost.from_post(group=feed_group.group, post=post).put()