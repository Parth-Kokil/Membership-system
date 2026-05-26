from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import jwt
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Membership System")

# =============== ADD THIS CORS CONFIGURATION ===============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],           # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],           # Allows all headers
)
# ==========================================================

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_12345")
ALGORITHM = "HS256"

def get_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

# ====================== MODELS ======================
class RegisterRequest(BaseModel):
    name: str
    username: str
    email: str
    password: str
    mobile_no: str

class LoginRequest(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    mobile_no: str
    membership_type: str

class OTPVerifyRequest(BaseModel):
    mobile_no: str
    otp_code: str
    membership_type: str

# ====================== HELPERS ======================
def generate_otp():
    return str(random.randint(100000, 999999))

def create_jwt_token(user_id: int, username: str):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ====================== ROUTES ======================

@app.post("/register")
def register(user: RegisterRequest, db=Depends(get_db)):
    try:
        hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO users (name, username, email, password_hash, mobile_no)
                VALUES (%s, %s, %s, %s, %s) RETURNING id, registered_at
            """, (user.name, user.username, user.email, hashed_pw.decode('utf-8'), user.mobile_no))
            result = cur.fetchone()
            db.commit()

        return {
            "message": "User registered successfully",
            "user_id": result["id"],
            "registered_at": result["registered_at"]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username/Email/Mobile already exists")

@app.post("/login")
def login(login_data: LoginRequest, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, username, password_hash FROM users 
                WHERE username = %s
            """, (login_data.username,))
            user = cur.fetchone()

            if not user or not bcrypt.checkpw(login_data.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            token = create_jwt_token(user['id'], user['username'])
            return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Protected Route Example
@app.get("/protected")
def protected_route(current_user=Depends(verify_jwt)):
    return {"message": f"Welcome {current_user['username']}! You are authenticated."}

# OTP Routes (You can protect them later if needed)
@app.post("/membership/request-otp")
def request_otp(request: OTPRequest, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE mobile_no = %s", (request.mobile_no,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found")

            otp = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=10)

            cur.execute("""
                INSERT INTO otps (mobile_no, otp_code, purpose, membership_type, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (request.mobile_no, otp, 'membership_verification', request.membership_type, expires_at))
            db.commit()

        print(f"🔐 OTP for {request.mobile_no} (Membership: {request.membership_type}): {otp}")
        return {"message": "OTP generated successfully. Check terminal."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/membership/verify")
def verify_membership(request: OTPVerifyRequest, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT * FROM otps 
                WHERE mobile_no = %s AND otp_code = %s AND expires_at > NOW()
            """, (request.mobile_no, request.otp_code))
            
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Invalid or expired OTP")

            cur.execute("SELECT id FROM users WHERE mobile_no = %s", (request.mobile_no,))
            user = cur.fetchone()

            expires_at = datetime.now() + timedelta(days=30)

            cur.execute("""
                INSERT INTO memberships (user_id, membership_type, status, activated_at, expires_at)
                VALUES (%s, %s, 'active', NOW(), %s)
            """, (user['id'], request.membership_type, expires_at))

            cur.execute("DELETE FROM otps WHERE mobile_no = %s", (request.mobile_no,))
            db.commit()

        return {"success": True, "message": "Membership activated successfully!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
def home():
    return {"message": "✅ Membership System with JWT is running"}