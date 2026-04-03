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
    comment: str = Field(..., min_length=20)
    photos: List[str] = Field(..., min_length=1)

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

# ==================== Government Officials Models ====================
BANNED_GOV_CATEGORIES = [
    "fsb", "fso", "svr", "gru", "mindefense", "rosgvardia_spec",
    "military", "intelligence", "counterintel", "special_forces",
    "classified", "strategic_command", "nuclear", "cyber_command",
]
BANNED_GOV_KEYWORDS = [
    "фсб", "фсо", "свр", "гру", "разведк", "контрразвед",
    "спецслужб", "спецназ", "секретн", "минобороны", "генштаб",
    "военн", "росгвардия", "нацгвардия", "ядерн", "стратегич",
]

ALLOWED_GOV_CATEGORIES = {
    "healthcare": "Здравоохранение",
    "education": "Образование",
    "mfc": "МФЦ / Госуслуги",
    "zags": "ЗАГС",
    "tax": "Налоговая (ФНС)",
    "court": "Суды",
    "police_local": "Полиция (участковые)",
    "gibdd": "ГИБДД",
    "housing": "ЖКХ / Управление домом",
    "administration": "Администрация",
    "social": "Соцзащита",
    "pension": "Пенсионный фонд",
    "employment": "Служба занятости",
    "transport": "Транспорт / Дорожные службы",
    "ecology": "Экология / Природнадзор",
}

class GovOfficialCreate(BaseModel):
    name: str = Field(..., min_length=2)
    position: str = Field(..., min_length=3)
    department: str = Field(..., min_length=3)
    gov_category: str
    region: Optional[str] = None

class GovReviewCreate(BaseModel):
    official_id: str
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=20)
    rating: int = Field(ge=1, le=5)
    category: str = "service_quality"

# ==================== People's Councils Models ====================
COUNCIL_LEVELS = {
    "yard": {"name": "Дворовый совет", "order": 1, "min_members": 3, "reps": 10},
    "village": {"name": "Сельский совет", "order": 2, "min_members": 5, "reps": 10},
    "district": {"name": "Районный совет", "order": 2, "min_members": 10, "reps": 10},
    "city": {"name": "Городской совет", "order": 3, "min_members": 25, "reps": 10},
    "republic": {"name": "Республиканский совет", "order": 4, "min_members": 50, "reps": 10},
    "okrug": {"name": "Совет федерального округа", "order": 5, "min_members": 50, "reps": 10},
    "country": {"name": "Народный совет РФ", "order": 6, "min_members": 80, "reps": 10},
}

COUNCIL_CREATION_CONFIRMATIONS_REQUIRED = 10

class CouncilCreate(BaseModel):
    name: str = Field(..., min_length=3)
    level: str
    description: str = Field(..., min_length=10)
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    legal_consent: bool = False

class DiscussionCreate(BaseModel):
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=20)
    category: str = "general"

class VoteCreate(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    options: List[str] = Field(..., min_length=2, max_length=10)

class CouncilNewsCreate(BaseModel):
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=20)
    repost_from: Optional[str] = None

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
    logger.info(f"Auth session request received, session_id starts with: {session_id[:10]}...")
    async with httpx.AsyncClient(timeout=15.0) as client_http:
        resp = await client_http.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            logger.error(f"Emergent auth returned {resp.status_code}: {resp.text}")
            raise HTTPException(status_code=401, detail="Invalid session")
        data = resp.json()
    logger.info(f"Emergent auth returned user: {data.get('email', 'unknown')}")
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
    logger.info(f"Auth session created for user {user_id} ({email})")
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

# ==================== Verification Feed ====================
@api_router.get("/reviews/pending-verification")
async def pending_verification_feed(request: Request, limit: int = 20):
    user = await require_user(request)
    already_verified = await db.verifications.find(
        {"user_id": user["user_id"]}, {"review_id": 1, "_id": 0}
    ).to_list(1000)
    verified_ids = [v["review_id"] for v in already_verified]
    query = {
        "status": "pending",
        "user_id": {"$ne": user["user_id"]},
    }
    if verified_ids:
        query["review_id"] = {"$nin": verified_ids}
    reviews = await db.reviews.find(query, {"_id": 0}).sort("expires_at", 1).to_list(limit)
    return reviews

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
    # Adaptive timer based on active user count
    active_users = await db.users.count_documents({})
    if active_users < 50:
        expiry_hours = 72
    elif active_users < 200:
        expiry_hours = 48
    elif active_users < 1000:
        expiry_hours = 24
    else:
        expiry_hours = 12
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
        "expires_at": (now + timedelta(hours=expiry_hours)).isoformat()
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
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    if review["user_id"] == user["user_id"]:
        raise HTTPException(status_code=400, detail="Нельзя подтвердить свой отзыв")
    if review["status"] != "pending":
        raise HTTPException(status_code=400, detail="Отзыв уже обработан")
    existing = await db.verifications.find_one({"review_id": verification.review_id, "user_id": user["user_id"]}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже подтвердили этот отзыв")
    if not verification.photos or len(verification.photos) < 1:
        raise HTTPException(status_code=400, detail="Необходимо прикрепить минимум 1 фотографию как доказательство")
    if not verification.comment or len(verification.comment.strip()) < 20:
        raise HTTPException(status_code=400, detail="Комментарий должен содержать минимум 20 символов с описанием конкретного заведения")
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

# ==================== Verification System ====================
VERIFICATION_LEVELS = {
    "basic": {"name": "Базовый", "description": "Email/Google", "icon": "user", "color": "#6b7280"},
    "confirmed": {"name": "Подтверждённый", "description": "Яндекс ID / Банк ID", "icon": "shield-check", "color": "#3b82f6"},
    "verified": {"name": "Верифицированный", "description": "Паспорт + телефон", "icon": "shield", "color": "#10b981"},
}

@api_router.get("/verification/status")
async def get_verification_status(request: Request):
    user = await require_user(request)
    return {
        "level": user.get("verification_level", "basic"),
        "phone_verified": user.get("phone_verified", False),
        "passport_verified": user.get("passport_verified", False),
        "bank_id_verified": user.get("bank_id_verified", False),
        "yandex_id_verified": user.get("yandex_id_verified", False),
        "levels": VERIFICATION_LEVELS,
    }

@api_router.post("/verification/phone")
async def verify_phone(request: Request):
    user = await require_user(request)
    body = await request.json()
    phone = body.get("phone", "").strip()
    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Некорректный номер телефона")
    code = str(uuid.uuid4().int)[:6]
    await db.verification_codes.insert_one({
        "user_id": user["user_id"], "phone": phone, "code": code,
        "type": "phone", "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    })
    logger.info(f"Phone verification code for {user['user_id']}: {code}")
    return {"success": True, "message": "Код отправлен (в тестовом режиме код: " + code + ")"}

@api_router.post("/verification/phone/confirm")
async def confirm_phone(request: Request):
    user = await require_user(request)
    body = await request.json()
    code = body.get("code", "").strip()
    record = await db.verification_codes.find_one(
        {"user_id": user["user_id"], "code": code, "type": "phone"}, {"_id": 0}
    )
    if not record:
        raise HTTPException(status_code=400, detail="Неверный код")
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {
        "phone": record["phone"], "phone_verified": True
    }})
    await db.verification_codes.delete_many({"user_id": user["user_id"], "type": "phone"})
    level = await _compute_verification_level(user["user_id"])
    return {"success": True, "verification_level": level}

@api_router.post("/verification/passport")
async def verify_passport(request: Request):
    user = await require_user(request)
    body = await request.json()
    full_name = body.get("full_name", "").strip()
    birth_date = body.get("birth_date", "").strip()
    series = body.get("series", "").strip()
    number = body.get("number", "").strip()
    if not all([full_name, birth_date, series, number]):
        raise HTTPException(status_code=400, detail="Заполните все поля")
    if len(series) != 4 or len(number) != 6:
        raise HTTPException(status_code=400, detail="Серия (4 цифры) и номер (6 цифр)")
    import hashlib
    passport_hash = hashlib.sha256(f"{series}{number}{birth_date}".encode()).hexdigest()
    existing = await db.users.find_one({"passport_hash": passport_hash, "user_id": {"$ne": user["user_id"]}}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Эти паспортные данные уже используются")
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {
        "passport_verified": True, "passport_hash": passport_hash,
        "passport_name": full_name, "passport_birth_date": birth_date
    }})
    level = await _compute_verification_level(user["user_id"])
    return {"success": True, "verification_level": level}

@api_router.post("/verification/bank-id")
async def verify_bank_id(request: Request):
    user = await require_user(request)
    body = await request.json()
    bank = body.get("bank", "sber")
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {
        "bank_id_verified": True, "bank_id_provider": bank
    }})
    level = await _compute_verification_level(user["user_id"])
    logger.info(f"Bank ID verified for {user['user_id']} via {bank}")
    return {"success": True, "verification_level": level, "message": f"Банк ID ({bank}) подтверждён"}

@api_router.post("/verification/yandex-id")
async def verify_yandex_id(request: Request):
    user = await require_user(request)
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {"yandex_id_verified": True}})
    level = await _compute_verification_level(user["user_id"])
    return {"success": True, "verification_level": level}

async def _compute_verification_level(user_id: str) -> str:
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if user.get("passport_verified") and user.get("phone_verified"):
        level = "verified"
    elif user.get("bank_id_verified") or user.get("yandex_id_verified"):
        level = "confirmed"
    else:
        level = "basic"
    await db.users.update_one({"user_id": user_id}, {"$set": {"verification_level": level}})
    return level

# ==================== News Feed ====================
@api_router.get("/news")
async def list_news(level: Optional[str] = None, category: Optional[str] = None, limit: int = 30):
    query = {}
    if level:
        query["level"] = level
    if category:
        query["category"] = category
    articles = await db.news.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return articles

@api_router.get("/news/{article_id}")
async def get_news_article(article_id: str):
    article = await db.news.find_one({"article_id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Not found")
    await db.news.update_one({"article_id": article_id}, {"$inc": {"views": 1}})
    return article

@api_router.post("/news")
async def create_news(request: Request):
    user = await require_user(request)
    body = await request.json()
    title = body.get("title", "").strip()
    content = body.get("content", "").strip()
    level = body.get("level", "city")
    category = body.get("category", "general")
    photos = body.get("photos", [])
    is_urgent = body.get("is_urgent", False)
    if not title or not content:
        raise HTTPException(status_code=400, detail="Заголовок и содержание обязательны")
    article_id = f"news_{uuid.uuid4().hex[:12]}"
    await db.news.insert_one({
        "article_id": article_id,
        "user_id": user["user_id"],
        "user_name": user.get("name", ""),
        "user_picture": user.get("picture", ""),
        "user_points": user.get("points", 0),
        "title": title, "content": content,
        "level": level, "category": category,
        "photos": photos, "is_urgent": is_urgent,
        "views": 0, "likes": 0, "comments_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    created = await db.news.find_one({"article_id": article_id}, {"_id": 0})
    return created

@api_router.post("/news/{article_id}/like")
async def like_news(request: Request, article_id: str):
    user = await require_user(request)
    existing = await db.news_likes.find_one({"article_id": article_id, "user_id": user["user_id"]})
    if existing:
        await db.news_likes.delete_one({"article_id": article_id, "user_id": user["user_id"]})
        await db.news.update_one({"article_id": article_id}, {"$inc": {"likes": -1}})
        return {"liked": False}
    await db.news_likes.insert_one({"article_id": article_id, "user_id": user["user_id"]})
    await db.news.update_one({"article_id": article_id}, {"$inc": {"likes": 1}})
    return {"liked": True}

@api_router.get("/news/{article_id}/comments")
async def get_news_comments(article_id: str):
    comments = await db.news_comments.find({"article_id": article_id}, {"_id": 0}).sort("created_at", 1).to_list(100)
    return comments

@api_router.post("/news/{article_id}/comments")
async def add_news_comment(request: Request, article_id: str):
    user = await require_user(request)
    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Комментарий не может быть пустым")
    comment_id = f"nc_{uuid.uuid4().hex[:12]}"
    await db.news_comments.insert_one({
        "comment_id": comment_id, "article_id": article_id,
        "user_id": user["user_id"], "user_name": user.get("name", ""),
        "user_picture": user.get("picture", ""), "user_points": user.get("points", 0),
        "text": text, "created_at": datetime.now(timezone.utc).isoformat()
    })
    await db.news.update_one({"article_id": article_id}, {"$inc": {"comments_count": 1}})
    return {"success": True, "comment_id": comment_id}

# ==================== Info Widgets (Weather, Currency, UV, Magnetic) ====================
@api_router.get("/widgets/weather")
async def get_weather(lat: float = 43.023, lon: float = 44.682):
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,uv_index&daily=temperature_2m_max,temperature_2m_min,weather_code,uv_index_max&timezone=auto&forecast_days=3")
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.error(f"Weather API error: {e}")
    raise HTTPException(status_code=503, detail="Сервис погоды недоступен")

@api_router.get("/widgets/currency")
async def get_currency():
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get("https://www.cbr-xml-daily.ru/daily_json.js")
            if resp.status_code == 200:
                data = resp.json()
                valutes = data.get("Valute", {})
                result = {}
                for code in ["USD", "EUR", "CNY", "GBP", "TRY"]:
                    if code in valutes:
                        v = valutes[code]
                        result[code] = {"name": v["Name"], "value": v["Value"], "previous": v["Previous"], "nominal": v["Nominal"]}
                return {"date": data.get("Date", ""), "rates": result}
    except Exception as e:
        logger.error(f"Currency API error: {e}")
    raise HTTPException(status_code=503, detail="Сервис курсов недоступен")

@api_router.get("/widgets/magnetic")
async def get_magnetic_storms():
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")
            if resp.status_code == 200:
                data = resp.json()
                recent = data[-8:] if len(data) > 8 else data[1:]
                return {"data": [{"time": r[0], "kp": float(r[1]), "kp_str": r[2]} for r in recent if len(r) > 2]}
    except Exception as e:
        logger.error(f"Magnetic API error: {e}")
    raise HTTPException(status_code=503, detail="Сервис магнитных бурь недоступен")

@api_router.get("/widgets/locations")
async def search_locations(q: str = ""):
    if len(q) < 2:
        return []
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            resp = await c.get(f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=8&language=ru&format=json")
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                return [{"name": r.get("name", ""), "admin1": r.get("admin1", ""), "country": r.get("country", ""), "latitude": r.get("latitude"), "longitude": r.get("longitude")} for r in results]
    except Exception as e:
        logger.error(f"Location search error: {e}")
    return []

# ==================== Problems Map ====================
@api_router.get("/map/problems")
async def get_problems_map():
    reviews = await db.reviews.find(
        {"latitude": {"$ne": None}, "longitude": {"$ne": None}},
        {"_id": 0, "review_id": 1, "title": 1, "status": 1, "rating": 1,
         "latitude": 1, "longitude": 1, "org_name": 1, "created_at": 1,
         "verification_count": 1}
    ).sort("created_at", -1).to_list(500)
    return reviews

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
    await db.news.create_index([("level", 1), ("created_at", -1)])
    await db.news.create_index("article_id", unique=True)
    await db.news_comments.create_index("article_id")
    await db.support_tickets.create_index("user_id")
    await db.support_tickets.create_index("ticket_id", unique=True)
    await db.support_tickets.create_index([("status", 1), ("updated_at", -1)])
    await db.daily_missions.create_index([("user_id", 1), ("date", 1)])
    await db.gov_officials.create_index("official_id", unique=True)
    await db.gov_officials.create_index("gov_category")
    await db.gov_reviews.create_index("official_id")
    await db.gov_reviews.create_index("review_id", unique=True)
    await db.councils.create_index("council_id", unique=True)
    await db.councils.create_index("level")
    await db.council_discussions.create_index("council_id")
    await db.council_discussions.create_index("discussion_id", unique=True)
    await db.council_votes.create_index("council_id")
    await db.council_votes.create_index("vote_id", unique=True)

    # Seed news
    news_count = await db.news.count_documents({})
    if news_count == 0:
        logger.info("Seeding news...")
        now = datetime.now(timezone.utc)
        seed_news = [
            {"article_id": "news_seed_001", "user_id": "seed_user_01", "user_name": "Алан М.", "user_picture": "", "user_points": 150,
             "title": "Ремонт дороги на ул. Ленина завершён", "content": "После многочисленных обращений граждан через Народный Контроль, администрация города наконец-то отремонтировала участок дороги на улице Ленина, 40-50. Ямы заделаны, положен новый асфальт. Благодарим всех, кто не остался равнодушным!",
             "level": "city", "category": "infrastructure", "photos": [], "is_urgent": False, "views": 234, "likes": 45, "comments_count": 12, "created_at": (now - timedelta(hours=6)).isoformat()},
            {"article_id": "news_seed_002", "user_id": "seed_user_02", "user_name": "Мария К.", "user_picture": "", "user_points": 80,
             "title": "Внимание! Просроченная продукция в сети магазинов", "content": "За последнюю неделю поступило более 15 отзывов о просроченной молочной продукции в нескольких магазинах города. Роспотребнадзор уже начал проверку. Будьте внимательны при покупках и проверяйте сроки годности!",
             "level": "city", "category": "health", "photos": [], "is_urgent": True, "views": 567, "likes": 89, "comments_count": 34, "created_at": (now - timedelta(hours=3)).isoformat()},
            {"article_id": "news_seed_003", "user_id": "seed_user_03", "user_name": "Георгий Т.", "user_picture": "", "user_points": 200,
             "title": "Субботник во дворе дома 15 по ул. Мира", "content": "Приглашаем всех жителей двора принять участие в субботнике в эту субботу в 10:00. Будем убирать территорию, красить бордюры и высаживать цветы. Инвентарь предоставляется. Все неравнодушные — добро пожаловать!",
             "level": "yard", "category": "community", "photos": [], "is_urgent": False, "views": 45, "likes": 18, "comments_count": 7, "created_at": (now - timedelta(hours=12)).isoformat()},
            {"article_id": "news_seed_004", "user_id": "seed_user_01", "user_name": "Алан М.", "user_picture": "", "user_points": 150,
             "title": "Новые тарифы ЖКХ: что изменится с марта", "content": "С 1 марта 2026 года вступают в силу новые тарифы на коммунальные услуги. Повышение составит от 3% до 8% в зависимости от категории услуг. Подробный разбор изменений и советы по экономии читайте в полном тексте.",
             "level": "republic", "category": "economics", "photos": [], "is_urgent": False, "views": 1230, "likes": 34, "comments_count": 56, "created_at": (now - timedelta(days=1)).isoformat()},
            {"article_id": "news_seed_005", "user_id": "seed_user_02", "user_name": "Мария К.", "user_picture": "", "user_points": 80,
             "title": "Открытие нового парка в Промышленном районе", "content": "В субботу состоится торжественное открытие нового парка отдыха в Промышленном районе. Площадь парка — 5 гектаров, есть детские и спортивные площадки, зоны для пикника. Вход свободный.",
             "level": "district", "category": "community", "photos": [], "is_urgent": False, "views": 89, "likes": 23, "comments_count": 5, "created_at": (now - timedelta(hours=18)).isoformat()},
        ]
        await db.news.insert_many(seed_news)
        logger.info(f"Seeded {len(seed_news)} news articles")

    # Ensure existing test users have referral_code and role
    await db.users.update_many(
        {"referral_code": {"$exists": False}},
        {"$set": {"referral_code": uuid.uuid4().hex[:8].upper(), "role": "user", "referred_by": None}}
    )

    # Start background task for expiring reviews
    asyncio.create_task(expire_reviews_task())
    logger.info("Review expiry background task started")

# ==================== Support Ticket System ====================
TICKET_CATEGORIES = ["bug", "complaint", "suggestion", "question", "rights_violation", "other"]
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]

FAQ_ITEMS = [
    {"question": "Как создать отзыв?", "answer": "Перейдите на страницу 'Отзыв' через меню навигации, выберите организацию, заполните форму и отправьте. Отзыв будет опубликован после получения 2 подтверждений от других пользователей."},
    {"question": "Как заработать баллы?", "answer": "Баллы начисляются за создание отзывов (10 баллов после верификации), подтверждение чужих отзывов (5 баллов) и использование реферального кода (25 баллов)."},
    {"question": "Что такое верификация личности?", "answer": "Верификация подтверждает вашу личность через телефон, паспорт или банковский ID. Это повышает доверие к вашим отзывам и открывает дополнительные функции."},
    {"question": "Как удалить свой аккаунт?", "answer": "Отправьте запрос через техподдержку с категорией 'Вопрос'. Мы обработаем запрос в течение 30 дней согласно 152-ФЗ."},
    {"question": "Куда обращаться при нарушении прав?", "answer": "Создайте тикет с категорией 'Нарушение прав'. Мы рассмотрим обращение в приоритетном порядке в течение 24 часов."},
    {"question": "Какие данные вы собираете?", "answer": "Мы собираем email, имя и фото из Google-аккаунта. При верификации — хэш паспортных данных и номер телефона. Подробнее в Политике конфиденциальности."},
    {"question": "Сколько времени рассматривается обращение?", "answer": "Стандартные обращения — до 48 часов. Нарушения прав и жалобы — до 24 часов. Предложения — до 7 рабочих дней."},
    {"question": "Почему мой отзыв истёк?", "answer": "Отзыв автоматически истекает через 24 часа, если не получит 2 подтверждения от других пользователей. Попробуйте создать отзыв заново."},
]

@api_router.get("/support/faq")
async def get_faq():
    return FAQ_ITEMS

@api_router.post("/support/tickets")
async def create_ticket(request: Request):
    user = await require_user(request)
    body = await request.json()
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()
    category = body.get("category", "question")
    if not subject or not message:
        raise HTTPException(status_code=400, detail="Тема и сообщение обязательны")
    if category not in TICKET_CATEGORIES:
        category = "other"
    ticket_id = f"ticket_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    priority = "high" if category in ["rights_violation", "complaint"] else "normal"
    await db.support_tickets.insert_one({
        "ticket_id": ticket_id,
        "user_id": user["user_id"],
        "user_name": user.get("name", ""),
        "user_email": user.get("email", ""),
        "subject": subject,
        "category": category,
        "status": "open",
        "priority": priority,
        "created_at": now,
        "updated_at": now,
        "messages": [{
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "user",
            "sender_name": user.get("name", ""),
            "text": message,
            "created_at": now,
        }],
    })
    await create_notification(user["user_id"], "ticket_created", "Обращение создано",
        f'Ваше обращение #{ticket_id[-6:]} принято. Мы ответим в течение 48 часов.', None)
    ticket = await db.support_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
    return ticket

@api_router.get("/support/tickets")
async def list_user_tickets(request: Request):
    user = await require_user(request)
    tickets = await db.support_tickets.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("updated_at", -1).to_list(50)
    return tickets

@api_router.get("/support/tickets/{ticket_id}")
async def get_ticket(request: Request, ticket_id: str):
    user = await require_user(request)
    ticket = await db.support_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Тикет не найден")
    if ticket["user_id"] != user["user_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")
    return ticket

@api_router.post("/support/tickets/{ticket_id}/reply")
async def reply_to_ticket(request: Request, ticket_id: str):
    user = await require_user(request)
    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Сообщение обязательно")
    ticket = await db.support_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Тикет не найден")
    if ticket["user_id"] != user["user_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")
    is_support = user.get("role") == "admin"
    msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:8]}",
        "sender": "support" if is_support else "user",
        "sender_name": "Техподдержка НК" if is_support else user.get("name", ""),
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    new_status = "in_progress" if is_support and ticket["status"] == "open" else ticket["status"]
    await db.support_tickets.update_one(
        {"ticket_id": ticket_id},
        {"$push": {"messages": msg}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat(), "status": new_status}}
    )
    if is_support:
        await create_notification(ticket["user_id"], "ticket_reply", "Ответ техподдержки",
            f'Получен ответ на обращение #{ticket_id[-6:]}', None)
    updated = await db.support_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
    return updated

@api_router.put("/support/tickets/{ticket_id}/status")
async def update_ticket_status(request: Request, ticket_id: str):
    user = await require_user(request)
    body = await request.json()
    new_status = body.get("status", "")
    if new_status not in TICKET_STATUSES:
        raise HTTPException(status_code=400, detail="Неверный статус")
    ticket = await db.support_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Тикет не найден")
    if user.get("role") != "admin" and not (ticket["user_id"] == user["user_id"] and new_status == "closed"):
        raise HTTPException(status_code=403, detail="Нет доступа")
    await db.support_tickets.update_one(
        {"ticket_id": ticket_id},
        {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True}

# Admin: list all tickets
@api_router.get("/admin/support/tickets")
async def admin_list_tickets(request: Request, status: Optional[str] = None):
    await require_admin(request)
    query = {}
    if status:
        query["status"] = status
    tickets = await db.support_tickets.find(query, {"_id": 0}).sort("updated_at", -1).to_list(200)
    return tickets

# ==================== Consent / Legal ====================
@api_router.post("/auth/consent")
async def record_consent(request: Request):
    user = await require_user(request)
    body = await request.json()
    consent_type = body.get("type", "terms_and_privacy")
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {
        "consent_accepted": True,
        "consent_type": consent_type,
        "consent_date": datetime.now(timezone.utc).isoformat(),
        "consent_ip": request.client.host if request.client else "unknown",
    }})
    return {"success": True}

@api_router.get("/legal/info")
async def get_legal_info():
    return {
        "operator_name": "ОсОО «Народный Контроль»",
        "inn": "Регистрация в ПВТ Кыргызской Республики",
        "ogrn": "",
        "legal_address": "720000, Кыргызская Республика, г. Бишкек, Парк Высоких Технологий",
        "email": "support@narodkontrol.kg",
        "phone": "+996 (000) 00-00-00",
        "age_restriction": "16+",
        "data_protection_officer": "Служба защиты данных платформы",
        "dpo_email": "privacy@narodkontrol.kg",
    }

# ==================== Onboarding ====================
@api_router.get("/onboarding/status")
async def get_onboarding_status(request: Request):
    user = await require_user(request)
    return {
        "completed": user.get("onboarding_completed", False),
        "step": user.get("onboarding_step", 0),
    }

@api_router.post("/onboarding/complete")
async def complete_onboarding(request: Request):
    user = await require_user(request)
    body = await request.json()
    step = body.get("step", 0)
    completed = body.get("completed", False)
    update = {"onboarding_step": step}
    if completed:
        update["onboarding_completed"] = True
        if not user.get("onboarding_completed"):
            await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": 20}})
            await create_notification(user["user_id"], "points_earned", "Бонус за знакомство!", "Вы получили 20 баллов за прохождение обучения")
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": update})
    return {"success": True}

# ==================== Verification Feed ====================
# ==================== Daily Missions & Streak ====================
DAILY_MISSION_TEMPLATES = [
    {"type": "verify", "title": "Подтвердите 2 отзыва", "description": "Помогите другим пользователям", "target": 2, "reward": 10, "icon": "shield-check"},
    {"type": "read_news", "title": "Прочитайте 3 новости", "description": "Будьте в курсе событий", "target": 3, "reward": 5, "icon": "newspaper"},
    {"type": "visit_map", "title": "Посетите карту проблем", "description": "Узнайте о проблемах рядом", "target": 1, "reward": 3, "icon": "map-pin"},
]

@api_router.get("/missions/daily")
async def get_daily_missions(request: Request):
    user = await require_user(request)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    missions = await db.daily_missions.find(
        {"user_id": user["user_id"], "date": today}, {"_id": 0}
    ).to_list(10)
    if not missions:
        missions = []
        for tmpl in DAILY_MISSION_TEMPLATES:
            m = {
                "mission_id": f"mission_{uuid.uuid4().hex[:8]}",
                "user_id": user["user_id"],
                "date": today,
                "type": tmpl["type"],
                "title": tmpl["title"],
                "description": tmpl["description"],
                "target": tmpl["target"],
                "progress": 0,
                "reward": tmpl["reward"],
                "icon": tmpl["icon"],
                "claimed": False,
            }
            missions.append(m)
        await db.daily_missions.insert_many([{**m} for m in missions])
    streak = user.get("streak_days", 0)
    last_active = user.get("last_active_date", "")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    if last_active == today:
        pass
    elif last_active == yesterday:
        streak += 1
        await db.users.update_one({"user_id": user["user_id"]}, {"$set": {"streak_days": streak, "last_active_date": today}})
    else:
        streak = 1
        await db.users.update_one({"user_id": user["user_id"]}, {"$set": {"streak_days": streak, "last_active_date": today}})
    return {"missions": missions, "streak": streak, "date": today}

@api_router.post("/missions/{mission_id}/progress")
async def update_mission_progress(request: Request, mission_id: str):
    user = await require_user(request)
    body = await request.json()
    increment = body.get("increment", 1)
    mission = await db.daily_missions.find_one(
        {"mission_id": mission_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not mission:
        raise HTTPException(status_code=404, detail="Миссия не найдена")
    new_progress = min(mission["progress"] + increment, mission["target"])
    await db.daily_missions.update_one(
        {"mission_id": mission_id},
        {"$set": {"progress": new_progress}}
    )
    return {"progress": new_progress, "target": mission["target"], "completed": new_progress >= mission["target"]}

@api_router.post("/missions/{mission_id}/claim")
async def claim_mission_reward(request: Request, mission_id: str):
    user = await require_user(request)
    mission = await db.daily_missions.find_one(
        {"mission_id": mission_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not mission:
        raise HTTPException(status_code=404, detail="Миссия не найдена")
    if mission["claimed"]:
        raise HTTPException(status_code=400, detail="Награда уже получена")
    if mission["progress"] < mission["target"]:
        raise HTTPException(status_code=400, detail="Миссия не выполнена")
    reward = mission["reward"]
    streak = user.get("streak_days", 1)
    bonus = reward if streak < 7 else int(reward * 1.5)
    await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": bonus}})
    await db.daily_missions.update_one({"mission_id": mission_id}, {"$set": {"claimed": True}})
    await create_notification(user["user_id"], "points_earned", "Миссия выполнена!",
        f'+{bonus} баллов за "{mission["title"]}"' + (f' (x1.5 за серию {streak} дней!)' if streak >= 7 else ''))
    return {"success": True, "reward": bonus, "streak_bonus": streak >= 7}

# ==================== Government Officials System ====================
def check_banned_gov(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in BANNED_GOV_KEYWORDS)

@api_router.get("/gov/categories")
async def get_gov_categories():
    return ALLOWED_GOV_CATEGORIES

@api_router.post("/gov/officials")
async def create_gov_official(request: Request, data: GovOfficialCreate):
    user = await require_user(request)
    if data.gov_category not in ALLOWED_GOV_CATEGORIES:
        raise HTTPException(status_code=400, detail="Недопустимая категория государственного органа")
    for field in [data.name, data.position, data.department]:
        if check_banned_gov(field):
            raise HTTPException(status_code=403, detail="Отзывы о сотрудниках силовых структур, спецслужб и органов с грифом секретности запрещены в соответствии с законодательством РФ")
    oid = f"gov_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    await db.gov_officials.insert_one({
        "official_id": oid, "name": data.name, "position": data.position,
        "department": data.department, "gov_category": data.gov_category,
        "region": data.region or "", "created_by": user["user_id"],
        "average_rating": 0, "review_count": 0, "created_at": now,
    })
    official = await db.gov_officials.find_one({"official_id": oid}, {"_id": 0})
    return official

@api_router.get("/gov/officials")
async def list_gov_officials(category: Optional[str] = None, q: Optional[str] = None):
    query = {}
    if category:
        query["gov_category"] = category
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"department": {"$regex": q, "$options": "i"}},
        ]
    officials = await db.gov_officials.find(query, {"_id": 0}).sort("review_count", -1).to_list(100)
    return officials

@api_router.get("/gov/officials/{official_id}")
async def get_gov_official(official_id: str):
    official = await db.gov_officials.find_one({"official_id": official_id}, {"_id": 0})
    if not official:
        raise HTTPException(status_code=404, detail="Служащий не найден")
    return official

@api_router.post("/gov/reviews")
async def create_gov_review(request: Request, data: GovReviewCreate):
    user = await require_user(request)
    official = await db.gov_officials.find_one({"official_id": data.official_id}, {"_id": 0})
    if not official:
        raise HTTPException(status_code=404, detail="Служащий не найден")
    if check_banned_gov(data.content) or check_banned_gov(data.title):
        raise HTTPException(status_code=403, detail="Контент содержит упоминания запрещённых структур")
    rid = f"govrev_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    await db.gov_reviews.insert_one({
        "review_id": rid, "official_id": data.official_id,
        "official_name": official["name"], "department": official["department"],
        "gov_category": official["gov_category"],
        "user_id": user["user_id"], "user_name": user.get("name", ""),
        "title": data.title, "content": data.content,
        "rating": data.rating, "category": data.category,
        "likes": 0, "created_at": now,
    })
    count = await db.gov_reviews.count_documents({"official_id": data.official_id})
    pipeline = [{"$match": {"official_id": data.official_id}}, {"$group": {"_id": None, "avg": {"$avg": "$rating"}}}]
    agg = await db.gov_reviews.aggregate(pipeline).to_list(1)
    avg = round(agg[0]["avg"], 1) if agg else 0
    await db.gov_officials.update_one({"official_id": data.official_id}, {"$set": {"review_count": count, "average_rating": avg}})
    await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": 8}})
    review = await db.gov_reviews.find_one({"review_id": rid}, {"_id": 0})
    return review

@api_router.get("/gov/reviews")
async def list_gov_reviews(official_id: Optional[str] = None, category: Optional[str] = None):
    query = {}
    if official_id:
        query["official_id"] = official_id
    if category:
        query["gov_category"] = category
    reviews = await db.gov_reviews.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return reviews

# ==================== People's Councils ====================
@api_router.get("/councils/levels")
async def get_council_levels():
    return COUNCIL_LEVELS

@api_router.post("/councils")
async def create_council(request: Request, data: CouncilCreate):
    user = await require_user(request)
    if data.level not in COUNCIL_LEVELS:
        raise HTTPException(status_code=400, detail="Неверный уровень совета")
    if not data.legal_consent:
        raise HTTPException(status_code=400, detail="Необходимо принять юридическое соглашение")
    cid = f"council_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    await db.councils.insert_one({
        "council_id": cid, "name": data.name, "level": data.level,
        "description": data.description, "address": data.address or "",
        "latitude": data.latitude, "longitude": data.longitude,
        "created_by": user["user_id"], "creator_name": user.get("name", ""),
        "members": [{"user_id": user["user_id"], "name": user.get("name", ""), "role": "chairman", "joined_at": now, "points": user.get("points", 0)}],
        "member_count": 1,
        "representatives": [],
        "rep_count": 0,
        "confirmations": [],
        "confirmations_needed": COUNCIL_CREATION_CONFIRMATIONS_REQUIRED,
        "confirmed": False,
        "discussion_count": 0, "vote_count": 0, "news_count": 0,
        "parent_council_id": None,
        "child_council_ids": [],
        "status": "pending_confirmation",
        "created_at": now,
        "legal_consent_by": user["user_id"],
        "legal_consent_at": now,
    })
    council = await db.councils.find_one({"council_id": cid}, {"_id": 0})
    return council

@api_router.post("/councils/{council_id}/confirm")
async def confirm_council_creation(request: Request, council_id: str):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    if council.get("confirmed"):
        raise HTTPException(status_code=400, detail="Совет уже подтверждён")
    # Check user verification level
    v_status = await db.verification_status.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not v_status or v_status.get("level", 0) < 2:
        raise HTTPException(status_code=403, detail="Только верифицированные пользователи (уровень 2+, паспорт) могут подтверждать создание советов")
    if any(c["user_id"] == user["user_id"] for c in council.get("confirmations", [])):
        raise HTTPException(status_code=400, detail="Вы уже подтвердили этот совет")
    if council["created_by"] == user["user_id"]:
        raise HTTPException(status_code=400, detail="Создатель не может подтвердить свой совет")
    now = datetime.now(timezone.utc).isoformat()
    conf = {"user_id": user["user_id"], "name": user.get("name", ""), "confirmed_at": now}
    new_count = len(council.get("confirmations", [])) + 1
    update = {"$push": {"confirmations": conf}}
    if new_count >= COUNCIL_CREATION_CONFIRMATIONS_REQUIRED:
        update["$set"] = {"confirmed": True, "status": "active", "confirmed_at": now}
    await db.councils.update_one({"council_id": council_id}, update)
    updated = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    return updated

@api_router.get("/councils")
async def list_councils(level: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if level:
        query["level"] = level
    if status:
        query["status"] = status
    else:
        query["status"] = {"$in": ["active", "pending_confirmation"]}
    councils = await db.councils.find(query, {"_id": 0}).sort("member_count", -1).to_list(100)
    return councils

@api_router.get("/councils/{council_id}")
async def get_council(council_id: str):
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    return council

@api_router.post("/councils/{council_id}/join")
async def join_council(request: Request, council_id: str):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    if any(m["user_id"] == user["user_id"] for m in council.get("members", [])):
        raise HTTPException(status_code=400, detail="Вы уже участник совета")
    now = datetime.now(timezone.utc).isoformat()
    await db.councils.update_one({"council_id": council_id}, {
        "$push": {"members": {"user_id": user["user_id"], "name": user.get("name", ""), "role": "member", "joined_at": now, "points": user.get("points", 0)}},
        "$inc": {"member_count": 1}
    })
    await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": 5}})
    return {"success": True}

@api_router.post("/councils/{council_id}/leave")
async def leave_council(request: Request, council_id: str):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    member = next((m for m in council.get("members", []) if m["user_id"] == user["user_id"]), None)
    if not member:
        raise HTTPException(status_code=400, detail="Вы не участник совета")
    if member["role"] == "chairman":
        raise HTTPException(status_code=400, detail="Председатель не может покинуть совет")
    await db.councils.update_one({"council_id": council_id}, {
        "$pull": {"members": {"user_id": user["user_id"]}, "representatives": {"user_id": user["user_id"]}},
        "$inc": {"member_count": -1}
    })
    return {"success": True}

# ==================== Council Representatives ====================
@api_router.post("/councils/{council_id}/nominate")
async def nominate_representative(request: Request, council_id: str):
    user = await require_user(request)
    body = await request.json()
    nominee_id = body.get("user_id", "")
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    if not any(m["user_id"] == user["user_id"] for m in council.get("members", [])):
        raise HTTPException(status_code=403, detail="Только участники могут номинировать")
    nominee = next((m for m in council.get("members", []) if m["user_id"] == nominee_id), None)
    if not nominee:
        raise HTTPException(status_code=400, detail="Номинант не является участником совета")
    # Check nominee has no bans
    nominee_user = await db.users.find_one({"user_id": nominee_id}, {"_id": 0})
    if nominee_user and nominee_user.get("banned"):
        raise HTTPException(status_code=400, detail="Пользователь заблокирован")
    existing = await db.council_nominations.find_one({
        "council_id": council_id, "nominee_id": nominee_id, "voter_id": user["user_id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже голосовали за этого кандидата")
    now = datetime.now(timezone.utc).isoformat()
    await db.council_nominations.insert_one({
        "council_id": council_id, "nominee_id": nominee_id,
        "nominee_name": nominee.get("name", ""),
        "voter_id": user["user_id"], "voter_name": user.get("name", ""),
        "created_at": now,
    })
    # Count votes for this nominee
    vote_count = await db.council_nominations.count_documents({"council_id": council_id, "nominee_id": nominee_id})
    return {"success": True, "nominee_votes": vote_count}

@api_router.get("/councils/{council_id}/nominations")
async def get_nominations(council_id: str):
    pipeline = [
        {"$match": {"council_id": council_id}},
        {"$group": {"_id": "$nominee_id", "name": {"$first": "$nominee_name"}, "votes": {"$sum": 1}}},
        {"$sort": {"votes": -1}},
        {"$limit": 20},
    ]
    results = await db.council_nominations.aggregate(pipeline).to_list(20)
    for r in results:
        r["user_id"] = r.pop("_id")
        u = await db.users.find_one({"user_id": r["user_id"]}, {"_id": 0, "points": 1, "rating_status": 1})
        r["points"] = u.get("points", 0) if u else 0
        r["rating_status"] = u.get("rating_status", "Новичок") if u else "Новичок"
    return results

@api_router.post("/councils/{council_id}/elect-representatives")
async def elect_representatives(request: Request, council_id: str):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    member = next((m for m in council.get("members", []) if m["user_id"] == user["user_id"]), None)
    if not member or member["role"] != "chairman":
        raise HTTPException(status_code=403, detail="Только председатель может провести выборы")
    pipeline = [
        {"$match": {"council_id": council_id}},
        {"$group": {"_id": "$nominee_id", "name": {"$first": "$nominee_name"}, "votes": {"$sum": 1}}},
        {"$sort": {"votes": -1}},
        {"$limit": 10},
    ]
    top = await db.council_nominations.aggregate(pipeline).to_list(10)
    reps = []
    for t in top:
        reps.append({"user_id": t["_id"], "name": t["name"], "votes": t["votes"], "elected_at": datetime.now(timezone.utc).isoformat()})
    await db.councils.update_one({"council_id": council_id}, {
        "$set": {"representatives": reps, "rep_count": len(reps)}
    })
    # Update member roles
    for rep in reps:
        await db.councils.update_one(
            {"council_id": council_id, "members.user_id": rep["user_id"]},
            {"$set": {"members.$.role": "representative"}}
        )
    return {"representatives": reps}

@api_router.post("/councils/{council_id}/complaint")
async def file_rep_complaint(request: Request, council_id: str):
    user = await require_user(request)
    body = await request.json()
    rep_id = body.get("representative_id", "")
    reason = body.get("reason", "").strip()
    if not reason or len(reason) < 10:
        raise HTTPException(status_code=400, detail="Причина жалобы — минимум 10 символов")
    now = datetime.now(timezone.utc).isoformat()
    cid = f"complaint_{uuid.uuid4().hex[:8]}"
    await db.council_complaints.insert_one({
        "complaint_id": cid, "council_id": council_id,
        "representative_id": rep_id, "complainant_id": user["user_id"],
        "complainant_name": user.get("name", ""), "reason": reason,
        "status": "open", "created_at": now,
    })
    return {"complaint_id": cid, "status": "open"}

# ==================== Council Discussions ====================
@api_router.post("/councils/{council_id}/discussions")
async def create_discussion(request: Request, council_id: str, data: DiscussionCreate):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    if not any(m["user_id"] == user["user_id"] for m in council.get("members", [])):
        raise HTTPException(status_code=403, detail="Только участники совета")
    did = f"disc_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    await db.council_discussions.insert_one({
        "discussion_id": did, "council_id": council_id, "council_name": council["name"],
        "author_id": user["user_id"], "author_name": user.get("name", ""),
        "title": data.title, "content": data.content, "category": data.category,
        "replies": [], "reply_count": 0, "likes": 0, "created_at": now,
    })
    await db.councils.update_one({"council_id": council_id}, {"$inc": {"discussion_count": 1}})
    await db.users.update_one({"user_id": user["user_id"]}, {"$inc": {"points": 3}})
    disc = await db.council_discussions.find_one({"discussion_id": did}, {"_id": 0})
    return disc

@api_router.get("/councils/{council_id}/discussions")
async def list_discussions(council_id: str):
    discs = await db.council_discussions.find({"council_id": council_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return discs

@api_router.post("/councils/{council_id}/discussions/{discussion_id}/reply")
async def reply_to_discussion(request: Request, council_id: str, discussion_id: str):
    user = await require_user(request)
    body = await request.json()
    text = body.get("text", "").strip()
    if not text or len(text) < 5:
        raise HTTPException(status_code=400, detail="Минимум 5 символов")
    now = datetime.now(timezone.utc).isoformat()
    reply = {"reply_id": f"reply_{uuid.uuid4().hex[:8]}", "author_id": user["user_id"],
             "author_name": user.get("name", ""), "text": text, "created_at": now}
    await db.council_discussions.update_one({"discussion_id": discussion_id},
        {"$push": {"replies": reply}, "$inc": {"reply_count": 1}})
    return reply

# ==================== Council Votes ====================
@api_router.post("/councils/{council_id}/votes")
async def create_vote(request: Request, council_id: str, data: VoteCreate):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    member = next((m for m in council.get("members", []) if m["user_id"] == user["user_id"]), None)
    if not member or member["role"] not in ["chairman", "representative"]:
        raise HTTPException(status_code=403, detail="Только председатель или представитель может создавать голосования")
    vid = f"vote_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    options = [{"option_id": f"opt_{i}", "text": o, "votes": 0, "voters": []} for i, o in enumerate(data.options)]
    await db.council_votes.insert_one({
        "vote_id": vid, "council_id": council_id, "council_name": council["name"],
        "author_id": user["user_id"], "author_name": user.get("name", ""),
        "title": data.title, "description": data.description,
        "options": options, "total_votes": 0,
        "status": "active", "created_at": now, "expires_at": expires,
    })
    await db.councils.update_one({"council_id": council_id}, {"$inc": {"vote_count": 1}})
    vote = await db.council_votes.find_one({"vote_id": vid}, {"_id": 0})
    return vote

@api_router.get("/councils/{council_id}/votes")
async def list_votes(council_id: str):
    votes = await db.council_votes.find({"council_id": council_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return votes

@api_router.post("/councils/{council_id}/votes/{vote_id}/cast")
async def cast_vote(request: Request, council_id: str, vote_id: str):
    user = await require_user(request)
    body = await request.json()
    option_id = body.get("option_id", "")
    vote = await db.council_votes.find_one({"vote_id": vote_id}, {"_id": 0})
    if not vote or vote["status"] != "active":
        raise HTTPException(status_code=404, detail="Голосование не найдено или завершено")
    for opt in vote["options"]:
        if user["user_id"] in opt.get("voters", []):
            raise HTTPException(status_code=400, detail="Вы уже проголосовали")
    await db.council_votes.update_one(
        {"vote_id": vote_id, "options.option_id": option_id},
        {"$inc": {"options.$.votes": 1, "total_votes": 1}, "$push": {"options.$.voters": user["user_id"]}}
    )
    return {"success": True}

# ==================== Council News + AI Moderation ====================
@api_router.post("/councils/{council_id}/news")
async def create_council_news(request: Request, council_id: str, data: CouncilNewsCreate):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404, detail="Совет не найден")
    is_rep = any(r["user_id"] == user["user_id"] for r in council.get("representatives", []))
    member = next((m for m in council.get("members", []) if m["user_id"] == user["user_id"]), None)
    is_chairman = member and member["role"] == "chairman"
    if not is_rep and not is_chairman:
        raise HTTPException(status_code=403, detail="Только представители или председатель могут публиковать новости")
    nid = f"cnews_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    ai_result = await _ai_check_news(data.title, data.content)
    status = "pending_moderation"
    await db.council_news.insert_one({
        "news_id": nid, "council_id": council_id, "council_name": council["name"],
        "council_level": council["level"],
        "author_id": user["user_id"], "author_name": user.get("name", ""),
        "title": data.title, "content": data.content,
        "repost_from": data.repost_from,
        "status": status,
        "ai_check": ai_result,
        "admin_verified": False,
        "created_at": now,
    })
    await db.councils.update_one({"council_id": council_id}, {"$inc": {"news_count": 1}})
    news = await db.council_news.find_one({"news_id": nid}, {"_id": 0})
    return news

async def _ai_check_news(title: str, content: str) -> dict:
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        llm_key = os.environ.get("EMERGENT_LLM_KEY", "")
        if not llm_key:
            return {"checked": False, "reason": "AI ключ не настроен"}
        chat = LlmChat(api_key=llm_key, model="gpt-4o-mini")
        prompt = f"""Ты — модератор платформы гражданского контроля. Проверь следующую новость на достоверность.

Заголовок: {title}
Содержание: {content}

Ответь строго в формате JSON:
{{"credibility": "high"|"medium"|"low"|"fake", "issues": ["список проблем если есть"], "summary": "краткий вывод на русском", "recommendation": "approve"|"review"|"reject"}}

Критерии:
- "fake" если явная дезинформация
- "low" если невозможно проверить или подозрительно
- "medium" если частично верно но требует проверки
- "high" если информация правдоподобна"""
        response = await asyncio.to_thread(chat.messages.create, messages=[UserMessage(content=prompt)])
        import json as jsonlib
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return {"checked": True, "result": jsonlib.loads(text.strip())}
    except Exception as e:
        return {"checked": False, "reason": str(e)[:200]}

@api_router.get("/councils/{council_id}/news")
async def list_council_news(council_id: str):
    news = await db.council_news.find({"council_id": council_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return news

@api_router.put("/councils/{council_id}/news/{news_id}/moderate")
async def moderate_council_news(request: Request, council_id: str, news_id: str):
    user = await require_user(request)
    if user.get("role") != "admin":
        council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
        if not council:
            raise HTTPException(status_code=404)
        is_rep = any(r["user_id"] == user["user_id"] for r in council.get("representatives", []))
        if not is_rep:
            raise HTTPException(status_code=403, detail="Только представители или админы")
    body = await request.json()
    action = body.get("action", "")
    if action == "approve":
        await db.council_news.update_one({"news_id": news_id}, {"$set": {"status": "verified", "admin_verified": True, "moderated_by": user["user_id"]}})
    elif action == "reject":
        await db.council_news.update_one({"news_id": news_id}, {"$set": {"status": "rejected", "admin_verified": True, "moderated_by": user["user_id"], "reject_reason": body.get("reason", "")}})
    elif action == "delete":
        await db.council_news.delete_one({"news_id": news_id})
        return {"deleted": True}
    return {"success": True}

@api_router.post("/councils/{council_id}/news/{news_id}/repost")
async def repost_council_news(request: Request, council_id: str, news_id: str):
    user = await require_user(request)
    council = await db.councils.find_one({"council_id": council_id}, {"_id": 0})
    if not council:
        raise HTTPException(status_code=404)
    is_rep = any(r["user_id"] == user["user_id"] for r in council.get("representatives", []))
    if not is_rep:
        raise HTTPException(status_code=403, detail="Только представители могут делать репосты")
    original = await db.council_news.find_one({"news_id": news_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404)
    body = await request.json()
    target_council_id = body.get("target_council_id", "")
    target = await db.councils.find_one({"council_id": target_council_id}, {"_id": 0})
    if not target:
        raise HTTPException(status_code=404, detail="Целевой совет не найден")
    nid = f"cnews_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    await db.council_news.insert_one({
        "news_id": nid, "council_id": target_council_id, "council_name": target["name"],
        "council_level": target["level"],
        "author_id": user["user_id"], "author_name": user.get("name", ""),
        "title": f"[Репост] {original['title']}", "content": original["content"],
        "repost_from": news_id, "original_council": original.get("council_name", ""),
        "status": "verified", "ai_check": original.get("ai_check", {}),
        "admin_verified": True, "created_at": now,
    })
    return {"success": True}

# ==================== Public Review (for sharing) ====================
@api_router.get("/reviews/{review_id}/public")
async def get_public_review(review_id: str):
    review = await db.reviews.find_one({"review_id": review_id, "status": "approved"}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден или не опубликован")
    return review

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
