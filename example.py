# JWT
import bcrypt
import jwt

with open("jwt-key.pub") as f:
    public_k = f.read()

with open("jwt-key") as f:
    private_k = f.read()

import datetime

# Create a Payload
payload = {"sub": 1, "iat": datetime.datetime.now().timestamp()}

# Sign it with my key
encoded = jwt.encode(payload, private_k, algorithm="RS256")

# Decode and verify the signature
decoded = jwt.decode(encoded,
                     public_k, algorithms=["RS256"])

# Encrypt a password
password = b"SUPER SECRET"
p2 = b"SOME OTHER THING"

hashed = bcrypt.hashpw(password, bcrypt.gensalt())
success = bcrypt.checkpw(p2, hashed)

assert success == False

# HTTP Response
response = {"access_token": encoded, }
assert "sub" in jwt.decode(response["access_token"],
                           public_k, algorithms=["RS256"])
