# Introduction to Auth
This projects is set to work with python `3.8`.

# Run Db and create tables
```
./run_db.sh
sleep 25
cat tables.sql | mysql --user=root --host=127.0.01 --port=3306 -proot;
```

# Run Web Server
```
python -m pip install -r requirements.txt
uvicorn app:app
```

*Authentication* -> Who are you?
*Authorization* -> What are you allowed to do?

### Create Key Pair for Signing
[Create](https://gist.github.com/rxm/6d5b51c5b947144e9e1ea6fcb8abb9ec) a private key first with openssl, then create a public key from that private key, make sure the keys are in `pem` format and that they are called `jwt-key` and `jwt-key.pub`.


### Signup

```sh
curl -H "Content-Type: application/json" -d '{"username":"david","password":"crossentropy"}' localhost:8000/signup | jq
```

### Authenticate

```sh
TKN=$(curl -H "Content-Type: application/json" -d '{"username":"david","password":"crossentropy"}' localhost:8000/authenticate | jq -r ".access_token")
echo $TKN
```

### Get Users 

```sh
curl -H "Authorization: Bearer $TKN" localhost:8000/user | jq;
```

### Get Protected
```sh
curl -H "Authorization: Bearer $TKN" localhost:8000/protected | jq;
```
