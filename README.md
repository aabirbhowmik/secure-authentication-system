# 🔐 Secure Authentication System

A secure RESTful Authentication API built using **Flask**, **PostgreSQL**, and **JWT**. This project demonstrates modern authentication practices including user registration, login, JWT-based authorization, profile management, password management, and role-based access control.

---

## 🚀 Features

### ✅ Authentication
- User Registration
- User Login
- JWT Authentication
- Refresh Access Token
- Logout
- Change Password
- Protected Routes

### ✅ User Profile
- View Profile
- Update Profile
- Delete Account

### 🚧 Upcoming Features
- Forgot Password (OTP Based)
- Role-Based Access Control (RBAC)
- Swagger API Documentation
- Deployment

---

## 🛠️ Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Flask-JWT-Extended
- Flask-Bcrypt
- python-dotenv

---

## 📁 Project Structure

```
Secure-Authentication-System/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── routes.py
├── requirements.txt
├── .gitignore
│
├── services/
└── utils/
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/aabirbhowmik/secure-authentication-system.git
```

Move into the project

```bash
cd secure-authentication-system
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=postgresql://username:password@localhost:5432/secure_db
```

Run the application

```bash
python app.py
```

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Register a new user |
| POST | /login | User login |
| POST | /refresh | Generate new access token |
| POST | /logout | Logout user |
| POST | /change-password | Change password |
| GET | /protected | Protected route |
| GET | /profile | View profile |
| PUT | /profile | Update profile |
| DELETE | /profile | Delete profile |

---

## 🔒 Authentication

Protected routes require a JWT access token.

Example header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 📈 Project Status

✅ Authentication Module Completed

✅ User Profile Module Completed

🚧 Forgot Password Module In Progress

---

## 👨‍💻 Author

**Aabir Bhowmik**
