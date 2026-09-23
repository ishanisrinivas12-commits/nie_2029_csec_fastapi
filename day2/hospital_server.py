from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# HOME
@app.get("/")
def home():
    return {"message": "City General Hospital Service Desk"}


# ---------------- DATABASE ----------------

users = {
    1: {
        "id": 1,
        "name": "Ananya Rao",
        "email": "ananya@hospital.com",
        "role": "Department Staff",
        "department": "Emergency",
        "password": "staff123",
        "status": "active"
    },
    2: {
        "id": 2,
        "name": "Rahul Kumar",
        "email": "rahul@hospital.com",
        "role": "Support Engineer",
        "department": "IT Support",
        "password": "engineer123",
        "status": "active"
    },
    3: {
        "id": 3,
        "name": "Priya Sharma",
        "email": "priya@hospital.com",
        "role": "Team Lead",
        "department": "Support Desk",
        "password": "lead123",
        "status": "active"
    },
    4: {
        "id": 4,
        "name": "Arjun Mehta",
        "email": "arjun@hospital.com",
        "role": "Admin",
        "department": "Administration",
        "password": "admin123",
        "status": "active"
    }
}


departments = {
    1: {
        "id": 1,
        "name": "Emergency",
        "location": "Ground Floor",
        "status": "active"
    },
    2: {
        "id": 2,
        "name": "Radiology",
        "location": "First Floor",
        "status": "active"
    },
    3: {
        "id": 3,
        "name": "Laboratory",
        "location": "First Floor",
        "status": "active"
    },
    4: {
        "id": 4,
        "name": "Pharmacy",
        "location": "Ground Floor",
        "status": "active"
    },
    5: {
        "id": 5,
        "name": "Administration",
        "location": "Second Floor",
        "status": "active"
    },
    6: {
        "id": 6,
        "name": "IT Support",
        "location": "Second Floor",
        "status": "active"
    }
}


categories = {
    1: {
        "id": 1,
        "name": "Equipment",
        "description": "Medical equipment and device related issues",
        "status": "active"
    },
    2: {
        "id": 2,
        "name": "Maintenance",
        "description": "Repair and maintenance related issues",
        "status": "active"
    },
    3: {
        "id": 3,
        "name": "IT",
        "description": "Computer, network, software and system issues",
        "status": "active"
    },
    4: {
        "id": 4,
        "name": "Facility",
        "description": "Electrical, plumbing, furniture and facility issues",
        "status": "active"
    }
}


requests = {
    1: {
        "id": 1,
        "requestId": "REQ001",
        "title": "ECG Machine Not Working",
        "description": "ECG machine is not powering on.",
        "department": "Emergency",
        "category": "Equipment",
        "priority": "High",
        "status": "Assigned",
        "raisedBy": "Ananya Rao",
        "assignedTo": "Rahul Kumar"
    },

    2: {
        "id": 2,
        "requestId": "REQ002",
        "title": "Computer Network Issue",
        "description": "Computer systems are unable to connect to the hospital network.",
        "department": "Radiology",
        "category": "IT",
        "priority": "Medium",
        "status": "In Progress",
        "raisedBy": "Radiology Staff",
        "assignedTo": "Rahul Kumar"
    },

    3: {
        "id": 3,
        "requestId": "REQ003",
        "title": "AC Not Working",
        "description": "Air conditioner is not functioning in the laboratory.",
        "department": "Laboratory",
        "category": "Facility",
        "priority": "Low",
        "status": "Open",
        "raisedBy": "Lab Staff",
        "assignedTo": None
    },

    4: {
        "id": 4,
        "requestId": "REQ004",
        "title": "Printer Maintenance",
        "description": "Pharmacy printer is producing unclear printouts.",
        "department": "Pharmacy",
        "category": "Maintenance",
        "priority": "Medium",
        "status": "Resolved",
        "raisedBy": "Pharmacy Staff",
        "assignedTo": "Rahul Kumar"
    }
}


# ---------------- SCHEMAS ----------------

class RequestCreate(BaseModel):
    title: str
    description: str
    department: str
    category: str
    priority: str
    status: str
    raisedBy: str
    assignedTo: str | None = None


class RequestResponse(RequestCreate):
    id: int
    requestId: str


# ---------------- USERS API ----------------

@app.get("/users")
def user_read_all():
    return list(users.values())


@app.get("/users/{id}")
def user_read_id(id: int):

    if id not in users:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )

    return users[id]


# ---------------- DEPARTMENTS API ----------------

@app.get("/departments")
def department_read_all():
    return list(departments.values())


@app.get("/departments/{id}")
def department_read_id(id: int):

    if id not in departments:
        raise HTTPException(
            status_code=404,
            detail="department not found"
        )

    return departments[id]


# ---------------- CATEGORIES API ----------------

@app.get("/categories")
def category_read_all():
    return list(categories.values())


@app.get("/categories/{id}")
def category_read_id(id: int):

    if id not in categories:
        raise HTTPException(
            status_code=404,
            detail="category not found"
        )

    return categories[id]


# ---------------- REQUEST APIs ----------------

@app.get("/requests")
def request_read_all():
    return list(requests.values())


@app.get("/requests/{id}")
def request_read_id(id: int):

    if id not in requests:
        raise HTTPException(
            status_code=404,
            detail="request not found"
        )

    return requests[id]


@app.post(
    "/requests",
    status_code=201,
    response_model=RequestResponse
)
def request_create(request_payload: RequestCreate):

    new_id = max(requests.keys(), default=0) + 1

    request_number = f"REQ{new_id:03d}"

    requests[new_id] = {
        "id": new_id,
        "requestId": request_number,
        **request_payload.model_dump()
    }

    return requests[new_id]


@app.put(
    "/requests/{id}",
    response_model=RequestResponse
)
def request_update(
    id: int,
    payload: RequestCreate
):

    if id not in requests:
        raise HTTPException(
            status_code=404,
            detail="request not found"
        )

    requests[id] = {
        "id": id,
        "requestId": requests[id]["requestId"],
        **payload.model_dump()
    }

    return requests[id]


@app.delete("/requests/{id}")
def request_delete(id: int):

    if id not in requests:
        raise HTTPException(
            status_code=404,
            detail="request not found"
        )

    del requests[id]

    return {
        "message": "request deleted successfully"
    }