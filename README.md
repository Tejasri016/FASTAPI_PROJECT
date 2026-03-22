
# 🏨 Hotel Room Booking System (FastAPI)

## 📌 Project Overview
This project is a backend system for managing hotel room bookings using FastAPI.  
It includes room management, booking workflows, filtering, searching, sorting, and pagination.

---

## 🚀 Features

- 🏨 Room Management (CRUD)
- 📅 Booking System
- 🔄 Check-in / Check-out Workflow
- 🔍 Search Functionality
- 📊 Sorting & Pagination
- 🎯 Filtering Rooms
- 🧾 Booking Tracking

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn

---

## ▶️ How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```
Run the server:
uvicorn main:app --reload
Open Swagger UI:
http://127.0.0.1:8000/docs

## 📚 API Endpoints
# 🏠 Basic
GET / → Welcome message


# 🏨 Rooms
GET /rooms
POST /rooms
GET /rooms/{room_id}
PUT /rooms/{room_id}
DELETE /rooms/{room_id}
GET /rooms/summary
GET /rooms/filter
GET /rooms/search
GET /rooms/sort
GET /rooms/page
GET /rooms/browse

## 📖 Bookings
GET /bookings
POST /bookings
GET /bookings/{booking_id}
GET /bookings/active
GET /bookings/search
GET /bookings/sort

## 🔄 Workflow
POST /checkin/{booking_id}
POST /checkout/{booking_id}

## 📌 Key Concepts Implemented
Pydantic validation
CRUD operations
Helper functions
Multi-step workflows
Search, sorting, pagination
Error handling using HTTPException
