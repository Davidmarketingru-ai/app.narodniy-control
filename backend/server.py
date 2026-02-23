from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, UploadFile, File
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import httpx
import asyncio
import shutil
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Uploads directory
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# ==================== Rating Statuses ====================
RATING_STATUSES = [
    {"name": "Новичок", "min_points": 0, "icon": "seedling", "color": "#6b7280"},
    {"name": "Наблюдатель", "min_points": 50, "icon": "eye", "color": "#3b82f6"},
    {"name": "Контролёр", "min_points": 150, "icon": "shield", "color": "#8b5cf6"},
    {"name": "Инспектор", "min_points": 350, "icon": "shield-check", "color": "#10b981"},
    {"name": "Эксперт", "min_points": 700, "icon": "award", "color": "#eab308"},
    {"name": "Мастер", "min_points": 1500, "icon": "crown", "color": "#f97316"},
    {"name": "Легенда", "min_points": 3000, "icon": "star", "color": "#ef4444"},
]

def get_user_status(points: int) -> dict:
    status = RATING_STATUSES[0]
    for s in RATING_STATUSES:
        if points >= s["min_points"]:
            status = s
    idx = RATING_STATUSES.index(status)
    next_status = RATING_STATUSES[idx + 1] if idx < len(RATING_STATUSES) - 1 else None
    return {
        "current": status,
        "level": idx + 1,
        "next": next_status,
        "progress": ((points - status["min_points"]) / (next_status["min_points"] - status["min_points"]) * 100) if next_status else 100,
    }

# ==================== Models ====================
class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    points: int = 0
    age_group: Optional[str] = "26-40"
    is_verified: bool = False
    theme: str = "dark"
    text_scale: int = 1
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    role: str = "user"
    created_at: Optional[str] = None

class OrganizationOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    org_id: str
    name: str
    category: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    average_rating: float = 0
    review_count: int = 0
    created_at: Optional[str] = None

class OrganizationCreate(BaseModel):
    name: str
    category: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class ReviewOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str
    user_id: str
    user_name: Optional[str] = None
    user_picture: Optional[str] = None
    org_id: str
    org_name: Optional[str] = None
    org_address: Optional[str] = None
    title: str
    content: str
    rating: int
    status: str = "pending"
    verification_count: int = 0
    photos: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    points_awarded: int = 0
    created_at: Optional[str] = None
    expires_at: Optional[str] = None

class ReviewCreate(BaseModel):
    org_id: str
    title: str
    content: str
    rating: int = Field(ge=1, le=5)
    photos: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class VerificationCreate(BaseModel):
    review_id: str
    comment: Optional[str] = None
    photos: List[str] = []

class NotificationOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str
    user_id: str
    type: str
    title: str
    message: Optional[str] = None
    is_read: bool = False
    review_id: Optional[str] = None
    created_at: Optional[str] = None

class RewardOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reward_id: str
    name: str
    description: str
    price: int
    icon: str
    age_groups: List[str]
    category: str

class PointsHistoryOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    history_id: str
    user_id: str
    amount: int
    reason: str
    created_at: Optional[str] = None

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age_group: Optional[str] = None
    theme: Optional[str] = None
    text_scale: Optional[int] = None

# ==================== Auth Helpers ====================
async def get_current_user(request: Request) -> Optional[dict]:
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    if not session_token:
        return None
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        return None
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user

async def require_user(request: Request) -> dict:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# ==================== Auth Routes ====================
@api_router.post("/auth/session")
async def auth_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    async with httpx.AsyncClient() as client_http:
        resp = await client_http.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        data = resp.json()
    email = data["email"]
    name = data.get("name", "")
    picture = data.get("picture", "")
    session_token = data["session_token"]
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one({"email": email}, {"$set": {"name": name, "picture": picture, "last_signed_in": datetime.now(timezone.utc).isoformat()}})
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        referral_code = uuid.uuid4().hex[:8].upper()
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "points": 0,
            "age_group": "26-40",
            "is_verified": False,
            "theme": "dark",
            "text_scale": 1,
            "referral_code": referral_code,
            "referred_by": None,
            "role": "user",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_signed_in": datetime.now(timezone.utc).isoformat()
        })
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    response.set_cookie(
        key="session_token", value=session_token,
        httponly=True, secure=True, samesite="none",
        path="/", max_age=7*24*60*60
    )
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user

@api_router.get("/auth/me")
async def auth_me(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@api_router.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie("session_token", path="/", secure=True, samesite="none")
    return {"success": True}

# ==================== User/Profile Routes ====================
@api_router.get("/profile", response_model=UserOut)
async def get_profile(request: Request):
    user = await require_user(request)
    return UserOut(**user)

@api_router.put("/profile")
async def update_profile(request: Request, update: ProfileUpdate):
    user = await require_user(request)
    updates = {k: v for k, v in update.model_dump().items() if v is not None}
    if updates:
        await db.users.update_one({"user_id": user["user_id"]}, {"$set": updates})
    updated = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return updated

# ==================== Organizations Routes ====================
@api_router.get("/organizations", response_model=List[OrganizationOut])
async def list_organizations():
    orgs = await db.organizations.find({}, {"_id": 0}).to_list(200)
    return [OrganizationOut(**o) for o in orgs]

@api_router.get("/organizations/{org_id}", response_model=OrganizationOut)
async def get_organization(org_id: str):
    org = await db.organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationOut(**org)

@api_router.post("/organizations", response_model=OrganizationOut)
async def create_organization(request: Request, org: OrganizationCreate):
    await require_user(request)
    org_id = f"org_{uuid.uuid4().hex[:12]}"
    doc = {
        "org_id": org_id,
        **org.model_dump(),
        "average_rating": 0,
        "review_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.organizations.insert_one(doc)
    created = await db.organizations.find_one({"org_id": org_id}, {"_id": 0})
    return OrganizationOut(**created)

# ==================== Reviews Routes ====================
@api_router.get("/reviews", response_model=List[ReviewOut])
async def list_reviews(status: Optional[str] = None, org_id: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if org_id:
        query["org_id"] = org_id
    reviews = await db.reviews.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [ReviewOut(**r) for r in reviews]

@api_router.get("/reviews/{review_id}", response_model=ReviewOut)
async def get_review(review_id: str):
    review = await db.reviews.find_one({"review_id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut(**review)

@api_router.post("/reviews", response_model=ReviewOut, status_code=201)
async def create_review(request: Request, review: ReviewCreate):
    user = await require_user(request)
    org = await db.organizations.find_one({"org_id": review.org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    review_id = f"rev_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    doc = {
        "review_id": review_id,
        "user_id": user["user_id"],
        "user_name": user.get("name", ""),
        "user_picture": user.get("picture", ""),
        "org_id": review.org_id,
        "org_name": org.get("name", ""),
        "org_address": org.get("address", ""),
        "title": review.title,
        "content": review.content,
        "rating": review.rating,
        "status": "pending",
        "verification_count": 0,
        "photos": review.photos,
        "latitude": review.latitude,
        "longitude": review.longitude,
        "points_awarded": 0,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=24)).isoformat()
    }
    await db.reviews.insert_one(doc)
    await db.organizations.update_one({"org_id": review.org_id}, {"$inc": {"review_count": 1}})
    await create_notification(user["user_id"], "review_created", "Отзыв создан", f'Ваш отзыв "{review.title}" отправлен на верификацию', review_id)
    created = await db.reviews.find_one({"review_id": review_id}, {"_id": 0})
    return ReviewOut(**created)

# ==================== Verifications Routes ====================
@api_router.post("/verifications")
async def create_verification(request: Request, verification: VerificationCreate):
    user = await require_user(request)
    review = await db.reviews.find_one({"review_id": verification.review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] == user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot verify own review")
    existing = await db.verifications.find_one({"review_id": verification.review_id, "user_id": user["user_id"]}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Already verified this review")
    ver_id = f"ver_{uuid.uuid4().hex[:12]}"
    await db.verifications.insert_one({
        "verification_id": ver_id,
        "review_id": verification.review_id,
        "user_id": user["user_id"],
        "user_name": user.get("name", ""),
        "comment": verification.comment,
        "photos": verification.photos,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    new_count = review["verification_count"] + 1
    update_data = {"verification_count": new_count}
    if new_count >= 2:
        update_data["status"] = "approved"
        points = 10
        await db.users.update_one({"user_id": review["user_id"]}, {"$inc": {"points": points}})
        await db.reviews.update_one({"review_id": verification.review_id}, {"$set": {"points_awarded": points}})
        await create_notification(review["user_id"], "review_verified", "Отзыв верифицирован!", f'Ваш отзыв получил {new_count} подтверждений и опубликован', verification.review_id)
        await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": 5}})
        await create_notification(user["user_id"], "points_earned", "Баллы начислены", "Вы получили 5 баллов за подтверждение отзыва", verification.review_id)
    else:
        await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": 5}})
        await create_notification(review["user_id"], "verification_received", "Подтверждение получено", f'Ваш отзыв получил подтверждение ({new_count}/2)', verification.review_id)
        await create_notification(user["user_id"], "points_earned", "Баллы начислены", "Вы получили 5 баллов за подтверждение отзыва", verification.review_id)
    await db.reviews.update_one({"review_id": verification.review_id}, {"$set": update_data})
    return {"success": True, "verification_id": ver_id, "new_count": new_count}

@api_router.get("/verifications/{review_id}")
async def get_verifications(review_id: str):
    vers = await db.verifications.find({"review_id": review_id}, {"_id": 0}).to_list(50)
    return vers

# ==================== Notifications Routes ====================
async def create_notification(user_id: str, ntype: str, title: str, message: str, review_id: str = None):
    nid = f"notif_{uuid.uuid4().hex[:12]}"
    await db.notifications.insert_one({
        "notification_id": nid,
        "user_id": user_id,
        "type": ntype,
        "title": title,
        "message": message,
        "is_read": False,
        "review_id": review_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

@api_router.get("/notifications", response_model=List[NotificationOut])
async def list_notifications(request: Request):
    user = await require_user(request)
    notifs = await db.notifications.find({"user_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return [NotificationOut(**n) for n in notifs]

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(request: Request, notification_id: str):
    await require_user(request)
    await db.notifications.update_one({"notification_id": notification_id}, {"$set": {"is_read": True}})
    return {"success": True}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(request: Request):
    user = await require_user(request)
    await db.notifications.update_many({"user_id": user["user_id"]}, {"$set": {"is_read": True}})
    return {"success": True}

# ==================== Points & Rewards Routes ====================
@api_router.get("/points/balance")
async def get_points_balance(request: Request):
    user = await require_user(request)
    return {"balance": user.get("points", 0)}

@api_router.get("/points/history", response_model=List[PointsHistoryOut])
async def get_points_history(request: Request):
    user = await require_user(request)
    history = await db.points_history.find({"user_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return [PointsHistoryOut(**h) for h in history]

@api_router.get("/rewards", response_model=List[RewardOut])
async def list_rewards(age_group: Optional[str] = None):
    query = {}
    if age_group:
        query["age_groups"] = age_group
    rewards = await db.rewards.find(query, {"_id": 0}).to_list(50)
    return [RewardOut(**r) for r in rewards]

@api_router.post("/rewards/{reward_id}/redeem")
async def redeem_reward(request: Request, reward_id: str):
    user = await require_user(request)
    reward = await db.rewards.find_one({"reward_id": reward_id}, {"_id": 0})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    if user.get("points", 0) < reward["price"]:
        raise HTTPException(status_code=400, detail="Insufficient points")
    await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": -reward["price"]}})
    hid = f"ph_{uuid.uuid4().hex[:12]}"
    await db.points_history.insert_one({
        "history_id": hid,
        "user_id": user["user_id"],
        "amount": -reward["price"],
        "reason": f"Обмен: {reward['name']}",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    await create_notification(user["user_id"], "reward_redeemed", "Награда получена!", f"Вы обменяли {reward['price']} баллов на \"{reward['name']}\"")
    return {"success": True, "message": f"Награда \"{reward['name']}\" получена!"}

# ==================== File Upload ====================
@api_router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    await require_user(request)
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".avi"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    file_id = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOADS_DIR / file_id
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    file_url = f"/api/uploads/{file_id}"
    return {"url": file_url, "filename": file_id}

@api_router.get("/uploads/{filename}")
async def get_upload(filename: str):
    from fastapi.responses import FileResponse
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp", ".mp4": "video/mp4", ".mov": "video/quicktime"}
    ext = Path(filename).suffix.lower()
    return FileResponse(file_path, media_type=media_types.get(ext, "application/octet-stream"))

# ==================== Rating Status ====================
@api_router.get("/rating/status")
async def get_rating_status(request: Request):
    user = await require_user(request)
    points = user.get("points", 0)
    status = get_user_status(points)
    reviews_count = await db.reviews.count_documents({"user_id": user["user_id"]})
    verifications_count = await db.verifications.count_documents({"user_id": user["user_id"]})
    return {
        **status,
        "points": points,
        "reviews_count": reviews_count,
        "verifications_count": verifications_count,
        "all_statuses": RATING_STATUSES,
    }

@api_router.get("/rating/leaderboard")
async def get_leaderboard():
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1, "picture": 1, "points": 1}).sort("points", -1).to_list(20)
    result = []
    for i, u in enumerate(users):
        status = get_user_status(u.get("points", 0))
        result.append({
            "rank": i + 1,
            "user_id": u["user_id"],
            "name": u.get("name", "Аноним"),
            "picture": u.get("picture", ""),
            "points": u.get("points", 0),
            "status": status["current"],
            "level": status["level"],
        })
    return result

# ==================== Referral System ====================
@api_router.post("/referral/apply")
async def apply_referral(request: Request):
    user = await require_user(request)
    body = await request.json()
    code = body.get("code", "").strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="Код не указан")
    if user.get("referred_by"):
        raise HTTPException(status_code=400, detail="Вы уже применили реферальный код")
    if user.get("referral_code") == code:
        raise HTTPException(status_code=400, detail="Нельзя использовать свой собственный код")
    referrer = await db.users.find_one({"referral_code": code}, {"_id": 0})
    if not referrer:
        raise HTTPException(status_code=404, detail="Реферальный код не найден")
    # Give bonus to both
    bonus_referrer = 50
    bonus_referred = 25
    await db.users.update_one({"user_id": referrer["user_id"]}, {"$inc": {"points": bonus_referrer}})
    await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": bonus_referred}, "$set": {"referred_by": referrer["user_id"]}})
    # Points history
    now_str = datetime.now(timezone.utc).isoformat()
    await db.points_history.insert_one({"history_id": f"ph_{uuid.uuid4().hex[:12]}", "user_id": referrer["user_id"], "amount": bonus_referrer, "reason": f"Реферальный бонус: {user.get('name', 'Пользователь')} зарегистрировался по вашему коду", "created_at": now_str})
    await db.points_history.insert_one({"history_id": f"ph_{uuid.uuid4().hex[:12]}", "user_id": user["user_id"], "amount": bonus_referred, "reason": f"Бонус за регистрацию по реферальному коду", "created_at": now_str})
    await create_notification(referrer["user_id"], "referral_bonus", "Реферальный бонус!", f'{user.get("name", "Пользователь")} зарегистрировался по вашему коду. +{bonus_referrer} баллов!')
    await create_notification(user["user_id"], "referral_bonus", "Бонус за реферала!", f'Вы получили {bonus_referred} баллов за использование реферального кода')
    return {"success": True, "bonus": bonus_referred, "message": f"Код активирован! +{bonus_referred} баллов"}

@api_router.get("/referral/stats")
async def get_referral_stats(request: Request):
    user = await require_user(request)
    referred_count = await db.users.count_documents({"referred_by": user["user_id"]})
    return {
        "referral_code": user.get("referral_code", ""),
        "referred_count": referred_count,
        "total_bonus": referred_count * 50,
    }

# ==================== Admin Routes ====================
async def require_admin(request: Request) -> dict:
    user = await require_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@api_router.get("/admin/reviews")
async def admin_list_reviews(request: Request, status: Optional[str] = None):
    await require_admin(request)
    query = {}
    if status:
        query["status"] = status
    reviews = await db.reviews.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)
    return reviews

@api_router.put("/admin/reviews/{review_id}/approve")
async def admin_approve_review(request: Request, review_id: str):
    await require_admin(request)
    review = await db.reviews.find_one({"review_id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.reviews.update_one({"review_id": review_id}, {"$set": {"status": "approved"}})
    points = 10
    await db.users.update_one({"user_id": review["user_id"]}, {"$inc": {"points": points}})
    await db.reviews.update_one({"review_id": review_id}, {"$set": {"points_awarded": points}})
    await create_notification(review["user_id"], "review_verified", "Отзыв одобрен модератором!", f'Ваш отзыв "{review["title"]}" одобрен. +{points} баллов', review_id)
    return {"success": True}

@api_router.put("/admin/reviews/{review_id}/reject")
async def admin_reject_review(request: Request, review_id: str):
    await require_admin(request)
    body = await request.json()
    reason = body.get("reason", "Не соответствует правилам")
    review = await db.reviews.find_one({"review_id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.reviews.update_one({"review_id": review_id}, {"$set": {"status": "rejected"}})
    await create_notification(review["user_id"], "review_rejected", "Отзыв отклонён", f'Ваш отзыв "{review["title"]}" отклонён. Причина: {reason}', review_id)
    return {"success": True}

@api_router.get("/admin/stats")
async def admin_stats(request: Request):
    await require_admin(request)
    total_users = await db.users.count_documents({})
    total_reviews = await db.reviews.count_documents({})
    pending_reviews = await db.reviews.count_documents({"status": "pending"})
    approved_reviews = await db.reviews.count_documents({"status": "approved"})
    rejected_reviews = await db.reviews.count_documents({"status": "rejected"})
    expired_reviews = await db.reviews.count_documents({"status": "expired"})
    total_orgs = await db.organizations.count_documents({})
    total_verifications = await db.verifications.count_documents({})
    return {
        "total_users": total_users,
        "total_reviews": total_reviews,
        "pending_reviews": pending_reviews,
        "approved_reviews": approved_reviews,
        "rejected_reviews": rejected_reviews,
        "expired_reviews": expired_reviews,
        "total_organizations": total_orgs,
        "total_verifications": total_verifications,
    }

@api_router.put("/admin/users/{user_id}/role")
async def admin_set_role(request: Request, user_id: str):
    await require_admin(request)
    body = await request.json()
    role = body.get("role", "user")
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    await db.users.update_one({"user_id": user_id}, {"$set": {"role": role}})
    return {"success": True}

@api_router.get("/admin/users")
async def admin_list_users(request: Request):
    await require_admin(request)
    users = await db.users.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return users

# ==================== Review Expiry Background Task ====================
async def expire_reviews_task():
    """Background task that marks expired pending reviews"""
    while True:
        try:
            now = datetime.now(timezone.utc).isoformat()
            expired = await db.reviews.find(
                {"status": "pending", "expires_at": {"$lt": now}}, {"_id": 0}
            ).to_list(100)
            for review in expired:
                await db.reviews.update_one(
                    {"review_id": review["review_id"]},
                    {"$set": {"status": "expired"}}
                )
                await create_notification(
                    review["user_id"], "review_expired",
                    "Отзыв истёк",
                    f'Ваш отзыв "{review["title"]}" не получил 2 подтверждения за 24 часа и был отклонён.',
                    review["review_id"]
                )
                logger.info(f"Expired review {review['review_id']}")
        except Exception as e:
            logger.error(f"Error in expire_reviews_task: {e}")
        await asyncio.sleep(300)  # Check every 5 minutes

# ==================== Seed Data ====================
@app.on_event("startup")
async def seed_data():
    org_count = await db.organizations.count_documents({})
    if org_count == 0:
        logger.info("Seeding organizations...")
        orgs = [
            {"org_id": "org_seed_001", "name": "Пятёрочка", "category": "shop", "address": "ул. Ленина, 44, Владикавказ", "latitude": 43.0248, "longitude": 44.6821, "description": "Сеть продуктовых магазинов", "average_rating": 3.2, "review_count": 5, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_002", "name": "Магнит", "category": "shop", "address": "пр. Мира, 28, Владикавказ", "latitude": 43.0195, "longitude": 44.6785, "description": "Продуктовый гипермаркет", "average_rating": 3.5, "review_count": 3, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_003", "name": "Кафе Арт", "category": "cafe", "address": "ул. Мира, 15, Владикавказ", "latitude": 43.0212, "longitude": 44.6843, "description": "Уютное кафе в центре", "average_rating": 4.1, "review_count": 2, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_004", "name": "Аптека 36.6", "category": "pharmacy", "address": "ул. Кирова, 10, Владикавказ", "latitude": 43.0180, "longitude": 44.6900, "description": "Круглосуточная аптека", "average_rating": 4.5, "review_count": 1, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_005", "name": "Ресторан Кавказ", "category": "restaurant", "address": "пр. Коста, 55, Владикавказ", "latitude": 43.0265, "longitude": 44.6760, "description": "Ресторан национальной кухни", "average_rating": 4.7, "review_count": 4, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_006", "name": "Перекрёсток", "category": "shop", "address": "ул. Маркуса, 22, Владикавказ", "latitude": 43.0155, "longitude": 44.6730, "description": "Супермаркет", "average_rating": 3.8, "review_count": 2, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_007", "name": "Кофейня Бариста", "category": "cafe", "address": "ул. Плиева, 5, Владикавказ", "latitude": 43.0230, "longitude": 44.6870, "description": "Авторский кофе и выпечка", "average_rating": 4.3, "review_count": 1, "created_at": datetime.now(timezone.utc).isoformat()},
            {"org_id": "org_seed_008", "name": "ТЦ Столица", "category": "entertainment", "address": "ул. Ватутина, 12, Владикавказ", "latitude": 43.0290, "longitude": 44.6810, "description": "Торговый центр", "average_rating": 3.9, "review_count": 3, "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        await db.organizations.insert_many(orgs)
        logger.info(f"Seeded {len(orgs)} organizations")

    review_count = await db.reviews.count_documents({})
    if review_count == 0:
        logger.info("Seeding reviews...")
        now = datetime.now(timezone.utc)
        reviews = [
            {"review_id": "rev_seed_001", "user_id": "seed_user_01", "user_name": "Алан М.", "user_picture": "", "org_id": "org_seed_001", "org_name": "Пятёрочка", "org_address": "ул. Ленина, 44", "title": "Просроченная молочная продукция", "content": "Обнаружил на полке молоко с истёкшим сроком годности на 3 дня. Срок годности — 15 января, а сегодня уже 18-е. Штрихкод и фото приложены.", "rating": 1, "status": "approved", "verification_count": 2, "photos": ["https://images.unsplash.com/photo-1576186726183-9bd8aa9fa6d9?w=400"], "latitude": 43.0248, "longitude": 44.6821, "points_awarded": 10, "created_at": (now - timedelta(hours=12)).isoformat(), "expires_at": (now + timedelta(hours=12)).isoformat()},
            {"review_id": "rev_seed_002", "user_id": "seed_user_02", "user_name": "Мария К.", "user_picture": "", "org_id": "org_seed_002", "org_name": "Магнит", "org_address": "пр. Мира, 28", "title": "Грязные полки в отделе овощей", "content": "Полки в отделе овощей и фруктов очень грязные, местами плесень. Персонал не реагирует на замечания.", "rating": 2, "status": "pending", "verification_count": 1, "photos": ["https://images.unsplash.com/photo-1760463921697-6ab2c0caca20?w=400"], "latitude": 43.0195, "longitude": 44.6785, "points_awarded": 0, "created_at": (now - timedelta(hours=6)).isoformat(), "expires_at": (now + timedelta(hours=18)).isoformat()},
            {"review_id": "rev_seed_003", "user_id": "seed_user_01", "user_name": "Алан М.", "user_picture": "", "org_id": "org_seed_004", "org_name": "Аптека 36.6", "org_address": "ул. Кирова, 10", "title": "Завышенные цены на лекарства", "content": "Цены на некоторые лекарства завышены в 2 раза по сравнению с аптеками рядом. Фото чека и сравнение цен приложены.", "rating": 2, "status": "pending", "verification_count": 0, "photos": [], "latitude": 43.0180, "longitude": 44.6900, "points_awarded": 0, "created_at": (now - timedelta(hours=2)).isoformat(), "expires_at": (now + timedelta(hours=22)).isoformat()},
            {"review_id": "rev_seed_004", "user_id": "seed_user_03", "user_name": "Георгий Т.", "user_picture": "", "org_id": "org_seed_005", "org_name": "Ресторан Кавказ", "org_address": "пр. Коста, 55", "title": "Отличное обслуживание!", "content": "Прекрасная кухня и отличный сервис. Официанты вежливые, еда свежая и вкусная. Рекомендую!", "rating": 5, "status": "approved", "verification_count": 3, "photos": [], "latitude": 43.0265, "longitude": 44.6760, "points_awarded": 10, "created_at": (now - timedelta(days=1)).isoformat(), "expires_at": (now).isoformat()},
            {"review_id": "rev_seed_005", "user_id": "seed_user_02", "user_name": "Мария К.", "user_picture": "", "org_id": "org_seed_006", "org_name": "Перекрёсток", "org_address": "ул. Маркуса, 22", "title": "Просроченный хлеб на полке", "content": "В отделе хлебобулочных изделий лежал хлеб с датой производства 5-дневной давности. Убрали только после жалобы.", "rating": 1, "status": "approved", "verification_count": 2, "photos": [], "latitude": 43.0155, "longitude": 44.6730, "points_awarded": 10, "created_at": (now - timedelta(days=2)).isoformat(), "expires_at": (now - timedelta(days=1)).isoformat()},
        ]
        await db.reviews.insert_many(reviews)
        logger.info(f"Seeded {len(reviews)} reviews")

    reward_count = await db.rewards.count_documents({})
    if reward_count == 0:
        logger.info("Seeding rewards...")
        rewards = [
            {"reward_id": "rw_001", "name": "Скидка на кино 20%", "description": "Скидка на билеты в кинотеатр", "price": 50, "icon": "film", "age_groups": ["18-25", "26-40"], "category": "entertainment"},
            {"reward_id": "rw_002", "name": "Бесплатный кофе", "description": "Бесплатный кофе в кафе-партнёре", "price": 30, "icon": "coffee", "age_groups": ["18-25", "26-40"], "category": "food"},
            {"reward_id": "rw_003", "name": "Скидка на доставку 50%", "description": "Скидка на первый заказ доставки", "price": 40, "icon": "truck", "age_groups": ["18-25"], "category": "delivery"},
            {"reward_id": "rw_004", "name": "Скидка на ресторан 15%", "description": "Скидка на ужин в ресторане-партнёре", "price": 100, "icon": "utensils", "age_groups": ["26-40", "41-60"], "category": "food"},
            {"reward_id": "rw_005", "name": "Юридическая консультация", "description": "Бесплатная 30-минутная консультация", "price": 150, "icon": "scale", "age_groups": ["26-40", "41-60"], "category": "services"},
            {"reward_id": "rw_006", "name": "Абонемент в фитнес (1 мес)", "description": "Бесплатный месяц в фитнес-клубе", "price": 200, "icon": "dumbbell", "age_groups": ["18-25", "26-40"], "category": "health"},
            {"reward_id": "rw_007", "name": "Скидка на аптеку 25%", "description": "Скидка на лекарства в аптеке-партнёре", "price": 80, "icon": "pill", "age_groups": ["41-60", "60+"], "category": "health"},
            {"reward_id": "rw_008", "name": "Бесплатная диагностика", "description": "Бесплатная диагностика в мед. центре", "price": 250, "icon": "stethoscope", "age_groups": ["41-60", "60+"], "category": "health"},
            {"reward_id": "rw_009", "name": "Скидка на продукты 20%", "description": "Скидка в магазинах-партнёрах", "price": 60, "icon": "shopping-cart", "age_groups": ["60+"], "category": "food"},
            {"reward_id": "rw_010", "name": "Бесплатная доставка", "description": "Бесплатная доставка лекарств и товаров", "price": 100, "icon": "package", "age_groups": ["60+"], "category": "delivery"},
            {"reward_id": "rw_011", "name": "Публикация без подтверждения", "description": "Опубликуйте отзыв без 2 подтверждений", "price": 500, "icon": "shield-check", "age_groups": ["18-25", "26-40", "41-60", "60+"], "category": "premium"},
        ]
        await db.rewards.insert_many(rewards)
        logger.info(f"Seeded {len(rewards)} rewards")

    await db.organizations.create_index("org_id", unique=True)
    await db.reviews.create_index("review_id", unique=True)
    await db.reviews.create_index("org_id")
    await db.reviews.create_index("user_id")
    await db.reviews.create_index([("status", 1), ("expires_at", 1)])
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("referral_code", unique=True, sparse=True)
    await db.user_sessions.create_index("session_token", unique=True)
    await db.notifications.create_index("user_id")
    await db.verifications.create_index("review_id")

    # Ensure existing test users have referral_code and role
    await db.users.update_many(
        {"referral_code": {"$exists": False}},
        {"$set": {"referral_code": uuid.uuid4().hex[:8].upper(), "role": "user", "referred_by": None}}
    )

    # Start background task for expiring reviews
    asyncio.create_task(expire_reviews_task())
    logger.info("Review expiry background task started")

# ==================== Health ====================
@api_router.get("/")
async def root():
    return {"message": "Народный Контроль API", "status": "running"}

@api_router.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(api_router)

cors_origins_env = os.environ.get('CORS_ORIGINS', '')
if cors_origins_env == '*' or not cors_origins_env:
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in cors_origins_env.split(',') if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
