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

  def getFeed(self):
    # Already cached?
    if self.parsedFeed:
      return self.parsedFeed

    self.feedModel.last_attempted_check = datetime.now()

    # Checking too often?
    if self.feedModel.last_successful_check and (datetime.now() - self.feedModel.last_successful_check) < timedelta(minutes = Reader.MIN_UPADTE_INTERVAL_MINUTES):
      logging.info("Did not fetch feed %s because it was checked in the last %s minutes.", self.feedModel.url, Reader.MIN_UPADTE_INTERVAL_MINUTES)
      self.feedModel.last_attempted_check_status = "Requesting feed too often."
      self.feedModel.put()
      return None

    # Make HTTP request
    logging.info("Fetching feed %s", self.feedModel.url)
    parsedFeed = None
    if self.feedModel.last_successful_check:
      parsedFeed = feedparser.parse(self.feedModel.url, etag=self.feedModel.last_etag,
          modified=self.feedModel.last_successful_check)
    else:
      parsedFeed = fe


  def saveMetadata(self, feed):
    self.feedModel.name = parsedFeed.feed.title
    self.feedModel.site_url = parsedFeed.feed.link
    self.feedModel.put()

  def savePosts(self, feed):
    # TODO: Move code

  def refreshFeed(self):
    feed = self.fetchFeed()

    if feed:
      self.saveMetadata(feed)
      self.savePosts(feed)

      updated_parsed_datetime = None
      if self.parsedFeed.feed.updated_parsed:
        updated_parsed_datetime = datetime.fromtimestamp(
            mktime(self.parsedFeed.feed.updated_parsed))
      # TODO: test that this loop doesn't happen if last_checked < updated
      # TODO: only update last_updated on success
      if (self.feedModel.last_successful_check is None) or (self.feedModel.last_successful_check < updated_parsed_datetime):
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
    self.feedModel.last_successful_check = datetime.now()
    if hasattr(self.parsedFeed, 'etag'):
      self.feedModel.last_etag = self.parsedFeed.etag
    self.feedModel.put()

  def createGroupPost(self, post, feed):
    for feed_group in feed.feed_groups:
      GroupPost.from_post(group=feed_group.group, post=post).put()