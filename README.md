# Membership System - Backend

A complete **Membership Management System** built with **FastAPI + PostgreSQL**.


##  Aim

To build a secure, scalable, and user-friendly backend system that allows users to register and activate different types of monthly memberships (like Gym, Shopping Discount, etc.) using **mobile number-based OTP verification**.

---

##  Purpose

The main purpose of this project is to demonstrate a real-world **membership management flow** where:
- Users can easily register.
- Membership activation is done securely through **OTP verification via mobile number only**.
- Admin/server and user side OTP matching ensures authenticity.
- All data is properly stored with timestamps for tracking.

This project simulates systems used by gyms, shopping clubs, subscription services, etc.

---

##  Advantages

- **Mobile-First Verification**: OTP verification is done only through mobile number (as per requirement).
- **Secure Authentication**: Uses JWT tokens + bcrypt password hashing.
- **Time Tracking**: Automatic registration timestamp and membership expiry.
- **Simple & Clean Architecture**: Easy to understand and extend.
- **Full-Stack Ready**: Comes with a simple frontend for easy testing.
- **Production Ready Structure**: Proper separation of concerns, error handling, and security.
- **Easy to Deploy**: Can be deployed on Render, Railway, AWS, etc.

---

## Features

### Backend Features
- User Registration with timestamp
- Secure Password Hashing (bcrypt)
- JWT Authentication (Login + Protected Routes)
- OTP Generation & Verification **(Mobile Number Only)**
- Membership Activation (30 days validity)
- Membership History
- PostgreSQL Database Integration

### Frontend
- Simple, clean HTML + Tailwind CSS UI

---

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT + HTTPBearer
- **Password Security**: bcrypt
- **Frontend**: HTML + Tailwind CSS


##  Project Structure

membership-app/
├── main.py                 # Main FastAPI backend
├── index.html              # Simple Frontend UI
├── .env                    # Environment variables (not pushed)
├── .gitignore
├── README.md
└── venv/                   # (ignored)
text


---

## ⚙️ How It Works (Backend Flow)

### 1. **User Registration**
- User sends details → Password hashed → Stored with `registered_at` timestamp.

### 2. **Login**
- Username + Password → Returns JWT Token.

### 3. **Membership Activation (Core Logic)**
- User requests OTP using **mobile number**.
- OTP stored in database (expires in 10 minutes).
- User submits OTP → Server verifies match → Membership activated for 30 days.

### 4. **Protected Routes**
- `/my-memberships` → Only accessible after login.

---

##  Database Tables

- `users` → User details + registration time
- `memberships` → Active/Expired memberships
- `otps` → Temporary OTP records

---

## 🚀 How to Run

### 1. Backend
 '''bash
cd membership-app
venv\Scripts\activate
uvicorn main:app --reload --port 8000

2. Frontend
Just open index.html in any browser.

📌 API Endpoints

Method, Endpoint,       Description,                              Protected
POST,  /register,     Register new user,                            No
POST,  /login,        Login & get JWT token,                        No
POST,  /membership    /request-otp,Request OTP for membership,      No
POST,  /membership    /verify,Verify OTP & activate membership ,    No
GET,  /my-memberships,  View user's membership history,            Yes

Security Features

Passwords are hashed (never stored in plain text)
JWT Token based authentication
OTP expires automatically
CORS enabled


📌 Future Improvements

Twilio / MSG91 SMS integration for real OTP
Admin Dashboard
Membership renewal system
Email notifications
