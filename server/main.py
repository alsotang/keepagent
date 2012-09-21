#! /usr/bin/env python
# coding=utf-8

import webapp2
import logging
import os
import json

from google.appengine.api import urlfetch

import lib

try: # detect it's on local or GAE
    isDev = os.environ['SERVER_SOFTWARE'].startswith('Dev')
except:
    isDev = False

logging.basicConfig(level=logging.INFO if not isDev else logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')

class MainPage(webapp2.RequestHandler):
    def get(self):
        text = '''<p>This version of keepagent server use <strong>%s</strong> protocol.</p>
        <p>请检查您的客户端是否使用了同一协议。</p>''' % lib.protocol

        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write(text)
    
    def post(self):
        req_body = lib.loadDict(self.request.body)

        logging.debug('request_body: %s', req_body)

        method = getattr(urlfetch, req_body.command)

        # 如超时则自动重试3次，3次失败后，GAE会抛错并返回给client 500错误。
        for dl in lib.deadlineRetry:
            try:
                res = urlfetch.fetch(req_body.path,
                                      lib.atob(req_body.payload),
                                      method,
                                      json.loads(req_body.headers),
                                     deadline=dl,
                                     )
            except urlfetch.DownloadError, e:
                logging.error(e)
            else:
                break #没有抛出任何异常则跳出循环

        result = {
            'status_code': res.status_code, # int
            # TODO: If there are multiple headers with the same name, their values will be joined into a single comma-separated string. If the values already contained commas (for example, Set-Cookie headers), you may want to use header_msg.get_headers(header_name) to retrieve a list of values instead.
            'headers': json.dumps(dict(res.headers)), 
            'content': lib.btoa(res.content), # str
        }

        logging.debug(result['status_code'])
        logging.debug(type(result['headers']))
        logging.debug(len(result['content']))

        result = lib.dumpDict(result)
        
        self.response.write(result)

app = webapp2.WSGIApplication([('/.*', MainPage)], debug = isDev)
