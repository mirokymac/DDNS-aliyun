#!/usr/bin/env python2
# -*- coding:utf-8 -*-


# main requirement for update
from urllib import urlencode, quote
from urllib2 import urlopen
from socket import create_connection as socket_create_connection
import time
from copy import deepcopy
from uuid import uuid1
from base64 import b64encode
from hmac import new as hmac_new
from hashlib import sha1
from json import loads as loadjson

# local run tracing
import logging
from logging import handlers
from sys import argv, exit
from getopt import getopt, GetoptError


HELP = "ddns-aliyun is a simple script to update your locale IP to \
aliyun DNS server.\npython ddns-aliyun.py [-c {configure path}]\n\
  -h\t\t\t Print out the help script.\n\
  -c\t\t\t set up the configure file, defualt:\"./token.json\"\n"
  
shortopts = 'hc:'
longopts = ['help', 'config']

url = 'http://alidns.aliyuncs.com'
ID = '' # AccessID 填入
Secret = '' # AccessSecret 填入
RequestId = ''
DomainName = '' # Domain 填入
SleepTime = 30


params = dict(
    Format='json',
    Version='2015-01-09',
    SignatureMethod='HMAC-SHA1',
    SignatureVersion='1.0',
)

CurrentIP = ''


def getDomainList(RRKey='', TypeKey='A', ValueKey=''):
    global DomainName
    p1 = deepcopy(params)
    t = time.gmtime()
    p1.update(dict(
        Action='DescribeDomainRecords',
        DomainName='%s' % topDomainName(DomainName),
        PageNumber=1,
        PageSize=500,
        RRKeyWord='%s' % RRKey,
        TypeKeyWord='%s' % TypeKey,
        ValueKeyWord='%s' % ValueKey,
        Timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', t),
        SignatureNonce=str(uuid1())
    ))
    p1.update(dict(
        Signature=sign(p1)
    ))
    rurl = url + '/?' + urlencode(p1)

    try:
        getjson = urlopen(rurl).read().decode('utf-8')
        logging.debug(getjson)
    except Exception as e:
        logging.error(
                '[' + str(e) + \
                ']Fail to get resolve list. Due to request failed.')
        return {}

    domainlist = dict()
    json = loadjson(getjson)
    try:
        for record in json['DomainRecords']['Record']:
            domainlist[record['RR']] = [record['RecordId'], record['Value']]
    except Exception as e:
        logging.error('[' + str(e) + '] Empty Domain List!')
        return {}

    return domainlist


def updateDomainRecord(recordID, ip, RR, Typekey='A'):
    p1 = deepcopy(params)
    t = time.gmtime()
    p1.update(dict(
        Action='UpdateDomainRecord',
        RecordId='%s' % recordID,
        RR='%s' % RR,
        Type='%s' % Typekey,
        Value='%s' % ip,
        TTL=600,
        Line='default',
        Timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', t),
        SignatureNonce=str(uuid1())
    ))

    if Typekey == 'mx':
        p1['Priority'] = 5

    p1['Signature'] = sign(p1)
    rurl = url + '/?' + urlencode(p1)
    logging.info(rurl)


    try:
        getjson = urlopen(rurl).read().decode('utf-8')
        logging.debug(getjson)
    except Exception as e:
        logging.error(str(e))
        logging.error('Fail to update Record. Due to request failed.')
        return False

    json = loadjson(getjson)
    try:
        if json['Code']:
            logging.error(
                    '[' + json['Code'] + \
                    ']Error occurred during updating record.'
                    )
            return False
    except Exception as e:
        logging.info('Update successful!')
        return True


def topDomainName(string):
    ss = string.split('.')
    return '%s.%s' % (ss[-2], ss[-1])


def sign(dict):
    global Secret
    str2sign = sorted(dict.iteritems(), key=lambda d: d[0])
    encodestring = 'GET&%2F&' + quote(urlencode(str2sign))
    encodestring = b64encode(hmac_new(Secret + '&', encodestring, sha1).digest())
    logging.debug(encodestring)

    return encodestring


def getip():
    sock = socket_create_connection(('ns1.dnspod.net', 6666), 20)
    ip = sock.recv(16)
    sock.close()
    return ip
  
    
# from shadowsocksr/shadowsocks/shell.py
def to_str(s):
    if bytes != str:
        if type(s) == bytes:
            return s.decode('utf-8')
    return s

def _decode_list(data):
    rv = []
    for item in data:
        if hasattr(item, 'encode'):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.items():
        if hasattr(value, 'encode'):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

class JSFormat:
    def __init__(self):
        self.state = 0

    def push(self, ch):
        ch = ord(ch)
        if self.state == 0:
            if ch == ord('"'):
                self.state = 1
                return to_str(chr(ch))
            elif ch == ord('/'):
                self.state = 3
            else:
                return to_str(chr(ch))
        elif self.state == 1:
            if ch == ord('"'):
                self.state = 0
                return to_str(chr(ch))
            elif ch == ord('\\'):
                self.state = 2
            return to_str(chr(ch))
        elif self.state == 2:
            self.state = 1
            if ch == ord('"'):
                return to_str(chr(ch))
            return "\\" + to_str(chr(ch))
        elif self.state == 3:
            if ch == ord('/'):
                self.state = 4
            else:
                return "/" + to_str(chr(ch))
        elif self.state == 4:
            if ch == ord('\n'):
                self.state = 0
                return "\n"
        return ""

def remove_comment(json):
    fmt = JSFormat()
    return "".join([fmt.push(c) for c in json])


def parse_json_in_str(data):
    # parse json and convert everything from unicode to str
    for st in ["\n", "\t", "\r"]:
        data = data.replace(st, "")
    return loadjson(data, object_hook=_decode_dict)


if __name__ == '__main__':
    
    logging.basicConfig(level=logging.WARNING,
            format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%d %b %Y %H:%M:%S')
    Rthandler = handlers.RotatingFileHandler(
            'ddns.log',
            maxBytes=10*1024*1024,
            backupCount=5
            )
    Rthandler.setLevel(logging.INFO)
    Rthandler.setFormatter(
            logging.Formatter(
                    '%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S'))
    logging.getLogger('').addHandler(Rthandler)
    
    try:
        optlist, argvs = getopt(argv[1: ], shortopts, longopts)
        from os import path
        if path.isfile("token.json"):
            with open("token.json") as jf:
                config = parse_json_in_str(
                        remove_comment(jf.read().decode("utf-8")))
                
                
        for key, value in optlist:
            if key in ("-h", "--help"):
                print HELP
                exit(0)
            if key in ("-c", "--config"):
                if path.isfile(value):
                    with open(value) as jf:
                        config = parse_json_in_str(
                                remove_comment(jf.read().decode("utf-8")))

        del path
        params.update(dict(AccessKeyId = config["ID"]))
        Secret = config["Secret"]
        RequestId = config["RequestId"]
        DomainName = config["DomainName"]
        SleepTime = config["SleepTime"]
        
        logging.info("Target Domain %s now checking..." % DomainName)
    except GetoptError as e:
        logging.error(e)
        exit(0)

#    print logging._handlerList
#    print config
        
    if Secret and DomainName and SleepTime:
#        print "on start"
        while True:
            if len(DomainName.split('.')) < 3:
                RR = '@'
            else:
                RR = DomainName.split('.')[0]
            if RequestId == '':
                try:
                    temp = getDomainList()[RR]
                except Exception as e:
                    logging.error('Fail to check domain, retrying...')
                    time.sleep(2* SleepTime)
 #                   print "rooting"
                    continue
                logging.info('Domain Check Done.')
                RequestId = temp[0]
                CurrentIP = temp[1]
                logging.debug("RequestID: %s\t CurrentIP: %s" % \
                              (RequestId, CurrentIP))
                del temp
    
            try:
                ip = getip()
                logging.info("CurrentIP: %s" % ip)
                if CurrentIP != ip:
                    if updateDomainRecord(RequestId, ip, RR):
                        CurrentIP = ip
            except Exception as e:
                logging.warning(str(e))
                logging.warning("Update Unsucessful")
                pass
            time.sleep(SleepTime)
    else:
        logging.error('No Token! Check you token config')
        exit(0)
