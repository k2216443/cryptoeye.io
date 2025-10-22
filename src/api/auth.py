import os
import base64
import hashlib
import json
import requests
from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from jose import jwt

# --------------------------------------------------------------------
# Environment variables required
# --------------------------------------------------------------------
COGNITO_DOMAIN = os.environ["COGNITO_DOMAIN"]              # e.g. chaineye-dev-auth.auth.eu-west-1.amazoncognito.com
CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
REGION = os.environ["AWS_REGION"]
REDIRECT_URI = os.environ["REDIRECT_URI"]                  # must match callback_urls
COGNITO_TOKEN_URL = f"https://{COGNITO_DOMAIN}/oauth2/token"
COGNITO_JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{COGNITO_DOMAIN.split('.')[0]}/.well-known/jwks.json"

# --------------------------------------------------------------------
# PKCE helpers
# --------------------------------------------------------------------
def gen_pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    return verifier, challenge

# --------------------------------------------------------------------
# App
# --------------------------------------------------------------------
app = FastAPI(title="Cognito OAuth Handler")

# Store temporary PKCE verifier per session (use proper session store in prod)
verifier_store = {}

@app.get("/auth/login")
def login():
    verifier, challenge = gen_pkce_pair()
    state = base64.urlsafe_b64encode(os.urandom(12)).decode()
    verifier_store[state] = verifier

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    url = f"https://{COGNITO_DOMAIN}/oauth2/authorize?" + urlencode(params)
    return RedirectResponse(url)

@app.get("/auth/callback")
def callback(request: Request, code: str, state: str):
    verifier = verifier_store.pop(state, None)
    if not verifier:
        raise HTTPException(status_code=400, detail="Invalid state")

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_resp = requests.post(COGNITO_TOKEN_URL, data=data, headers=headers, timeout=10)
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    tokens = token_resp.json()
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    # ----------------------------------------------------------------
    # Verify ID token signature and claims
    # ----------------------------------------------------------------
    jwks = requests.get(COGNITO_JWKS_URL, timeout=5).json()
    headers = jwt.get_unverified_header(id_token)
    key = next((k for k in jwks["keys"] if k["kid"] == headers["kid"]), None)
    if not key:
        raise HTTPException(status_code=400, detail="Invalid key id")

    try:
        payload = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            options={"verify_exp": True, "verify_aud": True},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token invalid: {e}")

    user_info = {
        "sub": payload["sub"],
        "email": payload.get("email"),
        "name": payload.get("name"),
        "given_name": payload.get("given_name"),
        "family_name": payload.get("family_name"),
        "picture": payload.get("picture"),
    }

    # Usually you create/load user profile here, set session cookie or JWT
    return JSONResponse(content={"ok": True, "user": user_info})
