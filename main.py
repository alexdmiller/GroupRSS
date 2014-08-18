#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import sys
sys.path.insert(0, 'libs')

import os
import webapp2
import jinja2
from reader import Reader
from models import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Handlers

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class FeedHandler(webapp2.RequestHandler):
  def get(self):
    feeds_query = Feed.all()
    template_values = {
      'feeds': feeds_query.run()
    }
    template = JINJA_ENVIRONMENT.get_template('feed.html')
    self.response.write(template.render(template_values))

  def post(self):
    feed_url = self.request.get('url')
    feed = Feed.get_by_key_name(feed_url)
    if feed is None:
      feed = Feed(key_name=feed_url,
                  url=feed_url)
      feed.put()

      reader = Reader(feed)
      reader.saveMetadata()
      reader.savePosts()

    self.redirect('/feed')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/feed', FeedHandler),
], debug=True)
