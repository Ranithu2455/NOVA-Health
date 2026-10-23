"""
NOVA Health backend (FastAPI), starter v0.1

Role: AI endpoints only. Supabase handles auth, profile, and tracking tables.
Every endpoint returns the format from docs/architecture/api-contract.md:
  success -> {"data": ...}      error -> {"error": {"code": ..., "message": ...}}

All AI endpoints return MOCK data for now so the Flutter team can connect today.
Swap each mock for the real call to ai-engine/engine.py later.
"""

import os
from datetime import date

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
DISCLAIMER = "This is guidance, not medical advice."

app = FastAPI(title="NOVA Health API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before the final demo
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# Error format (matches the API contract)
# ---------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    code = {400: "INVALID_INPUT", 401: "UNAUTHORIZED", 403: "FORBIDDEN",
            404: "NOT_FOUND", 422: "INVALID_INPUT"}.get(exc.status_code, "SERVER_ERROR")
    return JSONResponse(status_code=exc.status_code,
                        content={"error": {"code": code, "message": str(exc.detail)}})


# ---------------------------------------------------------------
# Auth: ask Supabase who owns this token
# ---------------------------------------------------------------
async def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split(" ", 1)[1]
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": SUPABASE_PUBLISHABLE_KEY},
        )
    if res.status_code != 200:
        raise HTTPException(401, "Invalid or expired token")
    return res.json()  # contains "id" and "email"


# ---------------------------------------------------------------
# Models
# ---------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


# ---------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------
@app.get("/health")
async def health():
    return {"data": {"status": "ok"}}


@app.get("/api/v1/me")
async def me(user: dict = Depends(current_user)):
    """Quick test that token checking works."""
    return {"data": {"id": user["id"], "email": user.get("email")}}


@app.post("/api/v1/assistant/chat")
async def chat(body: ChatRequest, user: dict = Depends(current_user)):
    if not body.message.strip():
        raise HTTPException(400, "message must not be empty")
    # TODO: replace with engine.answer_question(user["id"], body.message)
    reply = ("Your sleep averaged about 5.5 hours and water intake was low on several "
             "days. Try going to bed earlier and drinking more water.")
    return {"data": {"reply": f"{reply}\n\n{DISCLAIMER}", "sources": ["sleep", "water"]}}


@app.get("/api/v1/reports/daily")
async def daily_report(date_: date | None = None, user: dict = Depends(current_user)):
    # TODO: replace with engine.generate_daily_report(user["id"], date_)
    return {"data": {"date": (date_ or date.today()).isoformat(),
                     "report": f"Sample report: sleep was short and water was low today.\n\n{DISCLAIMER}"}}


@app.post("/api/v1/scan/prescription")
async def scan_prescription(image: UploadFile = File(...), user: dict = Depends(current_user)):
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    # TODO: OCR + vision model -> structured medications
    return {"data": {"scan_id": "mock-0001",
                     "medications": [{"name": "Sample Medicine", "dosage": "500 mg",
                                      "frequency": "twice daily", "duration_days": 10}],
                     "confidence": 0.86, "needs_user_confirmation": True}}


@app.post("/api/v1/scan/food")
async def scan_food(image: UploadFile = File(...), user: dict = Depends(current_user)):
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    # TODO: vision model -> nutrition estimate
    return {"data": {"description": "Rice and curry (sample)", "calories": 650,
                     "nutrients": {"protein_g": 20, "carbs_g": 90, "fat_g": 18},
                     "needs_user_confirmation": True}}


@app.post("/api/v1/emergency/trigger")
async def emergency_trigger(user: dict = Depends(current_user)):
    # TODO: notify emergency contacts (push/SMS) and log in audit_log
    return {"data": {"status": "triggered", "contacts_notified": 0}}
