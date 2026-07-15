from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from ..core.middleware import get_current_user
from ..core.google_calendar import GoogleCalendarService
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from datetime import datetime, timedelta
import os
import json
import secrets
import hashlib
import base64
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

def get_calendar_tokens_collection() -> AsyncIOMotorCollection:
    return db["google_calendar_tokens"]

@router.get("/authorize")
async def google_authorize(current_user = Depends(get_current_user)):
    try:
        calendar_service = GoogleCalendarService()
        flow = calendar_service.get_flow()

        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        flow.redirect_uri = redirect_uri

        print(f"Redirect URI: {redirect_uri}")

        # Generate PKCE code verifier and challenge
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().replace('=', '')

        # Store code verifier temporarily
        await db["temp_oauth_verifiers"].insert_one({
            "user_id": current_user["id"],
            "code_verifier": code_verifier,
            "expires_at": datetime.now() + timedelta(minutes=5)
        })

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )

        print(f"Authorization URL: {auth_url}")

        return {"authorization_url": auth_url}
    except Exception as e:
        print(f"Error in google_authorize: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def google_callback(request: Request, code: str = None, state: str = None, error: str = None):
    try:
        logger.info(f"Google callback received - Code: {code is not None}, Error: {error}, State: {state}")
        logger.info(f"Request URL: {request.url}")
        
        if error:
            logger.error(f"OAuth error from Google: {error}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(f"{frontend_url}/my-bookings/trainer?google_auth=error&message={error}")

        if not code:
            logger.error("No authorization code received from Google")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(f"{frontend_url}/my-bookings/trainer?google_auth=error&message=no_code")

        # Get the most recent code verifier
        verifier_record = await db["temp_oauth_verifiers"].find_one(
            {},
            sort=[("expires_at", -1)]
        )

        if not verifier_record:
            print("No code verifier found")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(f"{frontend_url}/my-bookings/trainer?google_auth=error")

        if verifier_record.get("expires_at") < datetime.now():
            print("Code verifier expired")
            await db["temp_oauth_verifiers"].delete_one({"_id": verifier_record["_id"]})
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(f"{frontend_url}/my-bookings/trainer?google_auth=error")

        code_verifier = verifier_record["code_verifier"]
        logger.info(f"Using code verifier for user: {verifier_record.get('user_id')}")

        calendar_service = GoogleCalendarService()
        flow = calendar_service.get_flow()

        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        flow.redirect_uri = redirect_uri
        logger.info(f"Using redirect URI: {redirect_uri}")

        # Exchange authorization code for credentials with code verifier
        logger.info("Attempting to fetch token with code verifier")
        flow.fetch_token(code=code, code_verifier=code_verifier)
        credentials = flow.credentials

        token_json = credentials.to_json()
        logger.info("OAuth callback received, token obtained successfully")

        await db["temp_oauth_verifiers"].delete_one({"_id": verifier_record["_id"]})

        temp_key = secrets.token_urlsafe(32)
        await db["temp_oauth_tokens"].insert_one({
            "key": temp_key,
            "token": token_json,
            "user_id": verifier_record.get("user_id"),
            "expires_at": datetime.now() + timedelta(minutes=5)
        })

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(f"{frontend_url}/my-bookings/trainer?google_auth=success&key={temp_key}")

    except Exception as e:
        print(f"Error in google_callback: {e}")
        import traceback
        traceback.print_exc()
        
        # Redirect to frontend with error
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        error_message = str(e) if e else "Unknown error"
        return RedirectResponse(f"{frontend_url}/my-bookings/trainer?google_auth=error&message={error_message}")

@router.post("/complete-auth")
async def complete_auth(request: Request, current_user = Depends(get_current_user), calendar_tokens_collection: AsyncIOMotorCollection = Depends(get_calendar_tokens_collection)):
    try:
        body = await request.json()
        key = body.get("key")

        print(f"Complete auth called with key: {key}")
        print(f"Current user: {current_user.get('id')}")

        if not key:
            print("No key provided in request body")
            raise HTTPException(status_code=400, detail="Key is required")

        # Get token from temporary storage
        temp_token = await db["temp_oauth_tokens"].find_one({"key": key})

        if not temp_token:
            print("Token not found in temporary storage")
            raise HTTPException(status_code=400, detail="Invalid or expired key")

        print(f"Temp token found, expires at: {temp_token.get('expires_at')}")

        # Check if expired
        if temp_token.get("expires_at") < datetime.now():
            print("Token expired")
            await db["temp_oauth_tokens"].delete_one({"key": key})
            raise HTTPException(status_code=400, detail="Key expired")

        token_json = json.loads(temp_token["token"])
        print("Token parsed successfully")

        # Check if token already exists for user
        existing = await calendar_tokens_collection.find_one({"user_id": current_user["id"]})

        if existing:
            print("Updating existing token")
            await calendar_tokens_collection.update_one(
                {"user_id": current_user["id"]},
                {
                    "$set": {
                        "google_token": json.dumps(token_json),
                        "calendar_enabled": True
                    }
                }
            )
        else:
            print("Creating new token entry")
            await calendar_tokens_collection.insert_one({
                "user_id": current_user["id"],
                "google_token": json.dumps(token_json),
                "calendar_enabled": True
            })

        await db["temp_oauth_tokens"].delete_one({"key": key})
        print("Temporary token deleted")

        return {"message": "Google Calendar connected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in complete_auth: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/disconnect")
async def disconnect_google_calendar(current_user = Depends(get_current_user), calendar_tokens_collection: AsyncIOMotorCollection = Depends(get_calendar_tokens_collection)):
    try:
        print(f"Disconnecting calendar for user: {current_user.get('id')}")
        result = await calendar_tokens_collection.delete_one({"user_id": current_user["id"]})
        print(f"Delete result: {result.deleted_count} documents deleted")

        return {"message": "Google Calendar disconnected successfully"}
    except Exception as e:
        print(f"Error disconnecting calendar: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_calendar_status(current_user = Depends(get_current_user), calendar_tokens_collection: AsyncIOMotorCollection = Depends(get_calendar_tokens_collection)):
    try:
        print(f"Checking calendar status for user: {current_user.get('id')}")
        token = await calendar_tokens_collection.find_one({"user_id": current_user["id"]})
        print(f"Token found: {token is not None}")
        return {
            "connected": token is not None,
            "calendar_enabled": token.get("calendar_enabled", False) if token else False
        }
    except Exception as e:
        print(f"Error checking calendar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
