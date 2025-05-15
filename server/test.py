from hashlib import sha256

s = '123'

password = sha256(s.encode('utf-8')).hexdigest()

print(password)
