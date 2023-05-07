from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def token(rollno,seconds):
    s=Serializer('hfbfe78hjef',seconds)
    return s.dumps({'user':rollno}).decode('utf-8')
