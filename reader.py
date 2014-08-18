import feedparser

class Reader:
  def __init__(self, feedModel):
    self.feedModel = feedModel
    self.feed = None

  def fetchFeed(self):
    if self.feed is None:
      self.feed = feedparser.parse(self.feedModel.url)

  def saveMetadata(self):
    self.fetchFeed()
    self.feedModel.name = self.feed["channel"]["title"]
    self.feedModel.put()

  def savePosts(self):
    self.fetchFeed()