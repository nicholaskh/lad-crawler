# -*- coding: utf-8 -*-

import random
import base64
from .settings import USER_AGENTS

from scrapy import signals


class NoincrementalSpiderMiddleware(object):

    def process_request(self, request, spider):
        agent = random.choice(USER_AGENTS)
        print("**************************" + agent)
        request.headers.setdefault('User-Agent', agent)
