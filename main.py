from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# ---------------- DATA ----------------

rooms = [
    {"id": 1, "room_number": "101", "type": "Single", "price_per_night": 1500, "floor": 1, "is_available": True},
    {"id": 2, "room_number": "102", "type": "Double", "price_per_night": 2500, "floor": 1, "is_available": True},
    {"id": 3, "room_number": "201", "type": "Suite",  "price_per_night": 5000, "floor": 2, "is_available": False},
    {"id": 4, "room_number": "202", "type": "Deluxe", "price_per_night": 4000, "floor": 2, "is_available": True},
    {"id": 5, "room_number": "301", "type": "Single", "price_per_night": 1800, "floor": 3, "is_available": True},
    {"id": 6, "room_number": "302", "type": "Double", "price_per_night": 2800, "floor": 3, "is_available": False},
]

bookings = []
booking_counter = 1

# ---------------- MODELS ----------------

class BookingRequest(BaseModel):
    guest_name: str = Field(..., min_length=2)
    room_id: int = Field(..., gt=0)
    nights: int = Field(..., gt=0, le=30)
    phone: str = Field(..., min_length=10)
    meal_plan: str = "none"
    early_checkout: bool = False

class NewRoom(BaseModel):
    room_number: str
    type: str = Field(..., min_length=2)
    price_per_night: int = Field(..., gt=0)
    floor: int = Field(..., gt=0)
    is_available: bool = True

# ---------------- HELPERS ----------------

def find_room(room_id):
    return next((r for r in rooms if r["id"] == room_id), None)

def calculate_stay_cost(price, nights, meal_plan, early_checkout):
    extra = 0
    if meal_plan == "breakfast":
        extra = 500
    elif meal_plan == "all-inclusive":
        extra = 1200

    total = (price + extra) * nights
    discount = 0

    if early_checkout:
        discount = total * 0.1
        total -= discount

    return int(total), int(discount)

def filter_rooms_logic(type=None, max_price=None, floor=None, is_available=None):
    result = rooms

    if type is not None:
        result = [r for r in result if r["type"].lower() == type.lower()]

    if max_price is not None:
        result = [r for r in result if r["price_per_night"] <= max_price]

    if floor is not None:
        result = [r for r in result if r["floor"] == floor]

    if is_available is not None:
        result = [r for r in result if r["is_available"] == is_available]

    return result

# ---------------- BASIC ----------------

@app.get("/")
def home():
    return {"message": "Welcome to Grand Stay Hotel"}

# ---------------- ROOMS ----------------

@app.get("/rooms")
def get_rooms():
    available = len([r for r in rooms if r["is_available"]])
    return {"rooms": rooms, "total": len(rooms), "available_count": available}

@app.get("/rooms/summary")
def rooms_summary():
    prices = [r["price_per_night"] for r in rooms]
    types = {}
    for r in rooms:
        types[r["type"]] = types.get(r["type"], 0) + 1

    return {
        "total": len(rooms),
        "available": len([r for r in rooms if r["is_available"]]),
        "occupied": len([r for r in rooms if not r["is_available"]]),
        "cheapest": min(prices),
        "expensive": max(prices),
        "type_breakdown": types
    }

@app.get("/rooms/filter")
def filter_rooms(type: str = None, max_price: int = None,
                 floor: int = None, is_available: bool = None):
    result = filter_rooms_logic(type, max_price, floor, is_available)
    return {"rooms": result, "count": len(result)}

@app.get("/rooms/search")
def search_rooms(keyword: str):
    result = [r for r in rooms if keyword.lower() in r["type"].lower()
              or keyword in r["room_number"]]

    if not result:
        return {"message": "No rooms found"}

    return {"results": result, "total": len(result)}

@app.get("/rooms/sort")
def sort_rooms(sort_by: str = "price_per_night", order: str = "asc"):
    if sort_by not in ["price_per_night", "floor", "type"]:
        raise HTTPException(400, "Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    return sorted(rooms, key=lambda r: r[sort_by], reverse=(order == "desc"))

@app.get("/rooms/page")
def paginate_rooms(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return {
        "page": page,
        "total_pages": -(-len(rooms) // limit),
        "rooms": rooms[start:start + limit]
    }

@app.get("/rooms/browse")
def browse_rooms(keyword: str = None, sort_by: str = "price_per_night",
                 order: str = "asc", page: int = 1, limit: int = 3):

    result = rooms

    if keyword:
        result = [r for r in result if keyword.lower() in r["type"].lower()]

    result = sorted(result, key=lambda r: r[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit

    return {
        "total": len(result),
        "page": page,
        "rooms": result[start:start + limit]
    }

@app.post("/rooms", status_code=201)
def add_room(room: NewRoom):
    if any(r["room_number"] == room.room_number for r in rooms):
        raise HTTPException(400, "Duplicate room number")

    new_room = {"id": len(rooms) + 1, **room.dict()}
    rooms.append(new_room)
    return new_room

# ❗ DYNAMIC ROUTES LAST

@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    return room

@app.put("/rooms/{room_id}")
def update_room(room_id: int, price_per_night: int = None, is_available: bool = None):
    room = find_room(room_id)
    if not room:
        raise HTTPException(404, "Not found")

    if price_per_night:
        room["price_per_night"] = price_per_night
    if is_available is not None:
        room["is_available"] = is_available

    return room

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(404, "Not found")

    if not room["is_available"]:
        raise HTTPException(400, "Room occupied")

    rooms.remove(room)
    return {"message": "Deleted"}

# ---------------- BOOKINGS ----------------

@app.get("/bookings")
def get_bookings():
    return {"bookings": bookings, "total": len(bookings)}

@app.get("/bookings/active")
def active_bookings():
    return [b for b in bookings if b["status"] in ["confirmed", "checked_in"]]

@app.get("/bookings/search")
def search_bookings(name: str):
    return [b for b in bookings if name.lower() in b["guest_name"].lower()]

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost"):
    return sorted(bookings, key=lambda b: b[sort_by])

@app.post("/bookings")
def create_booking(data: BookingRequest):
    global booking_counter

    room = find_room(data.room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    if not room["is_available"]:
        raise HTTPException(400, "Room occupied")

    total, discount = calculate_stay_cost(
        room["price_per_night"],
        data.nights,
        data.meal_plan,
        data.early_checkout
    )

    room["is_available"] = False

    booking = {
        "booking_id": booking_counter,
        "guest_name": data.guest_name,
        "room": room["room_number"],
        "nights": data.nights,
        "meal_plan": data.meal_plan,
        "total_cost": total,
        "discount": discount,
        "status": "confirmed"
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):
    for b in bookings:
        if b["booking_id"] == booking_id:
            return b
    raise HTTPException(404, "Booking not found")

# ---------------- WORKFLOW ----------------

@app.post("/checkin/{booking_id}")
def checkin(booking_id: int):
    for b in bookings:
        if b["booking_id"] == booking_id:
            b["status"] = "checked_in"
            return b
    raise HTTPException(404, "Not found")

@app.post("/checkout/{booking_id}")
def checkout(booking_id: int):
    for b in bookings:
        if b["booking_id"] == booking_id:
            b["status"] = "checked_out"
            room = next(r for r in rooms if r["room_number"] == b["room"])
            room["is_available"] = True
            return b
    raise HTTPException(404, "Not found")