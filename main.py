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
import os
import urllib
import webapp2
import jinja2
from google.appengine.ext import db

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class FeedHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {
      'test': 'HELLO WORLD'
    }
    template = JINJA_ENVIRONMENT.get_template('feed.html')
    self.response.write(template.render(template_values))

  def post(self):
    feed_url = self.request.get('feed_url')
    feed = Feed(key_name=feed_url)
    feed.put()

    template_values = {
      'test': 'HELLO WORLD'
    }
    template = JINJA_ENVIRONMENT.get_template('feed.html')
    self.response.write(template.render(template_values))

class Feed(db.Model):
  # ID
  name = db.StringProperty()
  last_checked = db.DateProperty()

class Post(db.Model):
  # ID of the feed that contains the post
  owner_feed_id = db.StringProperty()
  title = db.StringProperty()
  content = db.StringProperty()

class Group(db.Model):
  name = db.StringProperty()
  description = db.StringProperty()

class GroupPost(db.Model):
  owner_group_id = db.StringProperty()
  post_id = db.StringProperty()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/feed', FeedHandler),
], debug=True)
