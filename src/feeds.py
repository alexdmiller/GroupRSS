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
import webapp2
import jinja2
import time
from reader import Reader
from models import *
from slugify import slugify
from webapp2 import Route
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class FeedsHandler(webapp2.RequestHandler):
  def get_feed_info(self, feed_key_name):
    feed = Feed.get(feed_key_name);
    template_values = {
      'feed': feed
    }
    template = JINJA_ENVIRONMENT.get_template('templates/feed-info.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    Route(r'/feeds/<feed_key_name>', handler=FeedsHandler, handler_method='get_feed_info',
        methods=['GET'])
], debug=True)
