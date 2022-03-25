from mysql.connector import connect, Error
from fastapi import FastAPI, Depends, Header, HTTPException
import bcrypt
from pydantic import BaseModel
import bcrypt
import jwt
import datetime
from typing import Tuple


class UserPostModel(BaseModel):
    username: str
    password: str


class UserSignUpOut(BaseModel):
    id: int


def get_keys() -> Tuple[str, str]:
    "Reads private and public key from file."
    with open("./jwt-key.pub") as f:
        public_k = f.read()

    with open("./jwt-key") as f:
        private_k = f.read()

    return public_k, private_k


def marshall_user(user_tuple: Tuple[int, str, ]) -> dict:
    return {"id": user_tuple[0], "username": user_tuple[1]}


async def get_decoded(authorization: str = Header(...)) -> dict:
    """Gets decoded JSON payload from a bearer auth header.
    The subject of the JWT claims is cryptographically proven to be the bearer of the token.

    Args:
        authorization (str, optional): _description_. Defaults to Header(...).

    Raises:
        HTTPException: If decode fails or if scheme is not 'bearer'.

    Returns:
        dict: JSON payload that is verified.
    """
    try:
        header_split = authorization.split(" ")
        token_type, token = header_split[0], header_split[1]
        if token_type != "Bearer":
            raise HTTPException(
                status_code=400, detail="Only support bearer auth.")
        decoded = jwt.decode(token, public_k, algorithms=[JWT_ALGORITHM])
        return decoded
    except:
        raise HTTPException(
            status_code=403, detail="Not Authorized: Invalid token")


SALT = bcrypt.gensalt()
BCRYPT_SECRET = b"CARLOS_SAUL"
JWT_ALGORITHM = "RS256"
EXPIRY = datetime.timedelta(hours=48)

app = FastAPI()
public_k, private_k = get_keys()

# Don't do this in production, use SQLalchemy to handle connection pools
connection = connect(host="localhost", user="root",
                     port=3306, database="rbacpoc", password="root", autocommit=True)


@app.get("/user")
async def get_users(requestor: dict = Depends(get_decoded)):
    # We can trust that our payload has not been tampered with because of the signature.
    # We only return the user that corresponds to the sub(ject) of our payload
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id,username FROM user WHERE username='{requestor['sub']}';")
        results = [marshall_user(result) for result in cursor]
        return results


@app.post("/signup",
          response_model=UserSignUpOut,
          operation_id="user_sign_up_out",
          tags=["Users"])
async def sign_up_user(new_user: UserPostModel):

    username = new_user.username
    hashed_password = bcrypt.hashpw(
        new_user.password.encode(), SALT).decode('utf-8')

    with connection.cursor() as cursor:
        # Do Not Do This In Production, vulnerable to SQL Injection attacks.
        # If we send a JSON with {"username":"1; DROP DATABASE....;"} we could be in big trouble.
        cursor.execute(f"SELECT id FROM user WHERE username='{username}'")

        existing_user = []
        for user in cursor:
            existing_user.append(user)

        if len(existing_user) == 1:
            raise HTTPException(status_code=400, detail="User is not unique.")

    insert_stm = f"INSERT INTO user(username, password) VALUES ('{username}','{hashed_password}');"

    results = []
    with connection.cursor() as cursor:
        cursor.execute(insert_stm)
        cursor.execute(
            f"SELECT id FROM user WHERE user.username='{username}';")
        for result in cursor:
            results.append(result)

    return {"id": results[0][0]}


@app.post("/authenticate", operation_id="authenticate")
async def post_authenticate(user: UserPostModel):
    username = user.username
    password = user.password

    results = []
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT password FROM user WHERE user.username='{username}';")
        for result in cursor:
            results.append(result)
    # Get the first element of the first row returned from our SELECT statement.
    hashed_password = results[0][0]

    password_check_passed = bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()

    )

    if not password_check_passed:
        raise HTTPException(
            status_code=403, detail="Not Authorized")

    payload = {
        "username": username,
        "sub": username,
        "iat": datetime.datetime.now().timestamp(),
        "exp": datetime.datetime.now() + EXPIRY,
        "role": "ADMIN"
    }

    encoded = jwt.encode(payload, private_k, algorithm="RS256")

    return {"access_token": encoded}


@app.get("/protected", operation_id="protected_resource")
async def get_protected(requestor: dict = Depends(get_decoded)):
    subject = requestor["sub"]
    return {"message": f"Hello {subject}, I know that you are you, since I signed the token you are sending to me when you provided me with your unique private credentials."}


@app.on_event("shutdown")
def shutdown_event():
    connection.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
