import os
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from typing import Optional
import boto3
from dotenv import load_dotenv

import uvicorn


app = FastAPI(title="learn-fastapi-cloudauth")


load_dotenv()

USER_POOL_ID = os.environ.get("USER_POOL_ID")
REGION = os.environ.get("REGION")
CLIENT_ID = os.environ.get("CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET")

auth = Cognito(region=REGION, userPoolId=USER_POOL_ID, client_id=CLIENT_ID)


get_current_user = CognitoCurrentUser(
    region=REGION, userPoolId=USER_POOL_ID, client_id=CLIENT_ID
)


cognito_client = boto3.client("cognito-idp", region_name=REGION)


class TokenResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    confirmation_code: Optional[str] = None


class AccessUser(BaseModel):
    sub: str


# ROUTES
@app.get("/", dependencies=[Depends(auth.scope(["read:users"]))])
def secure():
    """Produces output for a valid access token (according to scope)"""
    # access token is valid
    return "Hello"


@app.post("/get-token", response_model=TokenResponse)
def get_token(user: User):
    """Start here to authenticate."""
    try:
        response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": user.username, "PASSWORD": user.password},
            ClientId=CLIENT_ID,
        )
        auth_res = response["AuthenticationResult"]
        ret = TokenResponse(
            access_token=auth_res["AccessToken"],
            id_token=auth_res["IdToken"],
            token_type=auth_res["TokenType"],
            expires_in=auth_res["ExpiresIn"],
            refresh_token=auth_res["RefreshToken"],
        )
        return ret
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/access/")
def secure_access(current_user: AccessUser = Depends(auth.claim(AccessUser))):
    """Access token is valid and getting user info from access token."""
    return "Hello", {current_user.sub}


@app.get("/user/")
def secure_user(current_user: CognitoClaims = Depends(get_current_user)):
    """ID token is valid and getting user info from ID token."""
    return {"message": f"Hello, {current_user.username}", "user_data": current_user}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
