#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from urllib import urlencode, quote
from urllib2 import urlopen
import socket
import time
from copy import deepcopy
from uuid import uuid1
from base64 import b64encode
import hmac
from hashlib import sha1
from json import loads as loadjson

url = 'http://alidns.aliyuncs.com'
ID = '' # AccessID 填入
Secret = '' # AccessSecret 填入
RequestId = ''
DomainName = '' # Domain 填入

params = dict(
    Format='json',
    Version='2015-01-09',
    AccessKeyId=ID,
    SignatureMethod='HMAC-SHA1',
    SignatureVersion='1.0',
)

CurrentIP = ''


def getDomainList(RRKey='', TypeKey='A', ValueKey=''):
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
        print getjson
    except Exception as e:
        print('[' + e + ']Fail to get resolve list. Due to request failed.')
        return False

    domainlist = dict()
    json = loadjson(getjson)
    try:
        for record in json['DomainRecords']['Record']:
            domainlist[record['RR']] = record['RecordId']
    except Exception as e:
        print('Empty List.')
        return False

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
    print(rurl)


    try:
        getjson = urlopen(rurl).read().decode('utf-8')
        print getjson
    except Exception as e:
        print('[' + e + ']Fail to update Record. Due to request failed.')
        return False

    json = loadjson(getjson)
    try:
        if json['Code']:
            print('[' + json['Code'] + ']Error occurred during updating record.')
            return False
    except Exception as e:
        print('Update successful.')
        return True


def topDomainName(string):
    ss = string.split('.')
    return '%s.%s' % (ss[-2], ss[-1])


def sign(dict):
    str2sign = sorted(dict.iteritems(), key=lambda d: d[0])
    encodestring = 'GET&%2F&' + quote(urlencode(str2sign))
    encodestring = b64encode(hmac.new(Secret + '&', encodestring, sha1).digest())
    print(encodestring)

    return encodestring


def getip():
    sock = socket.create_connection(('ns1.dnspod.net', 6666), 20)
    ip = sock.recv(16)
    sock.close()
    return ip


if __name__ == '__main__':
    while True:
        if DomainName.split('.').count() < 3:
            RR = '@'
        else:
            RR = DomainName.split('.')[0]

        if RequestId == '':
            RequestId = getDomainList()[RR]
            print(RequestId)

        try:
            ip = getip()
            print(ip)
            if CurrentIP != ip:
                if updateDomainRecord(RequestId, ip, RR):
                    CurrentIP = ip
        except Exception as e:
            print e
            pass
        time.sleep(30)
