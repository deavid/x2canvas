# encoding: UTF-8
import hashlib
import json, os
from binascii import unhexlify, hexlify, b2a_qp, a2b_qp
from base64 import b64encode, b64decode

def encode(encoding, text):
    if encoding == "quopri": return b2a_qp(text)
    if encoding == "hex": return hexlify(text)
    if encoding == "base64": return b64encode(text)
    raise ValueError("Unknown encoding %s" % encoding)

def decode(encoding, text):
    if encoding == "quopri": return a2b_qp(text)
    if encoding == "hex": return unhexlify(text)
    if encoding == "base64": return b64decode(text)
    raise ValueError("Unknown encoding %s" % encoding)

def compute_hash(passobj, cleartextpasswd):
    method = passobj.get("meth","plain")
    password_encoding = passobj.get("pw-enc","quopri")
    salt_encoding = passobj.get("salt-enc","hex")
    salt = decode(salt_encoding,passobj.get("salt",""))
    
    saltedpasswd = salt + str(cleartextpasswd)
    passwd = None
    if method == "plain": passwd = saltedpasswd
    if method == "md5": passwd = hashlib.md5(saltedpasswd).digest()
    if method == "sha1": passwd = hashlib.sha1(saltedpasswd).digest()
    if method == "sha224": passwd = hashlib.sha224(saltedpasswd).digest()
    if method == "sha256": passwd = hashlib.sha256(saltedpasswd).digest()
    if method == "sha384": passwd = hashlib.sha384(saltedpasswd).digest()
    if method == "sha512": passwd = hashlib.sha512(saltedpasswd).digest()
    if passwd is None:
        passwd = hashlib.new(method).update(saltedpasswd).digest()
    if passwd is None:
        raise ValueError, "Method not understood"
    return encode(password_encoding, passwd)
    
def check(jsontext, cleartextpasswd):
    passobj = json.loads(jsontext)
    passwd = passobj.get("passwd")
    computed_passwd = compute_hash(passobj, cleartextpasswd)
    return passwd == computed_passwd
    
def new(cleartextpasswd, **options):
    passobj = {
        'meth' : 'sha224',
        'pw-enc' : 'base64',
        'salt-enc' : 'base64',
        'salt-sz' : 6,
        'salt' : None,
    }
    for k,v in options.items():
        k = k.replace("_","-")
        if k not in passobj: 
            print "WARN: Ignored password option %s" % (repr(k))
            continue
        passobj[k] = v
    if passobj['salt'] is None:
        passobj['salt'] = os.urandom(passobj['salt-sz'])
    del passobj['salt-sz']
    passobj['salt'] = encode(passobj['salt-enc'],passobj['salt'])
    passobj['passwd'] = compute_hash(passobj,cleartextpasswd)
    return json.dumps(passobj)

