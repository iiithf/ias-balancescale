#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import optparse
import json
import csv


CURSOR = 0
INPUTS = []


def addr_parse(addr):
  i = addr.find(':')
  host = '' if i<0 else addr[0:i]
  port = int(addr if i<0 else addr[i+1:])
  return (host, port)


class RequestHandler(BaseHTTPRequestHandler):
  def body(self):
    size = int(self.headers.get('Content-Length'))
    return self.rfile.read(size)
  
  def body_json(self):
    return json.loads(self.body())

  def send(self, code, body=None, headers=None):
    self.send_response(code)
    for k, v in headers.items():
      self.send_header(k, v)
    self.end_headers()
    if body is not None:
      self.wfile.write(body)
  
  def send_json(self, code, body):
    heads = {'Content-Type': 'application/json'}
    self.send(code, bytes(json.dumps(body), 'utf8'), heads)

  def do_GET(self):
    global CURSOR, INPUTS
    example = INPUTS[CURSOR]
    CURSOR = (CURSOR+1) % len(INPUTS)
    request = {'examples': [example]}
    print('sending request', request)
    return self.send_json(200, request)


p = optparse.OptionParser()
p.set_defaults(address=':1994', dataset='balance-scale.data')
p.add_option('--address', dest='address', help='set input service address')
p.add_option('--dataset', dest='dataset', help='set dataset file')
(o, args) = p.parse_args()


print('reading dataset %s ...' % o.dataset)
with open(o.dataset, 'r') as f:
  for row in csv.reader(f):
    if len(row)==0: continue
    INPUTS.append({'left-weight': row[1], 'left-distance': row[2], 'right-weight': row[3], 'right-distance': row[4]})

addr = addr_parse(o.address)
print('starting input service on ', addr)
httpd = HTTPServer(addr, RequestHandler)
httpd.serve_forever()
