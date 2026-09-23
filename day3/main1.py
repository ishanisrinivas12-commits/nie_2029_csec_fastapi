from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from pymongo import MongoClient
from bson import ObjectId

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


# =================================================
# APP
# =================================================

app = FastAPI()


# =================================================
# MONGODB CONFIG
# =================================================

URL = "mongodb://127.0.0.1:27017"

client = MongoClient(URL)

db = client["hospital"]

requests_collection = db["requests"]
users_collection = db["users"]


# =================================================
# SECURITY CONFIG
# =================================================

password_hash = PasswordHash.recommended()

SECRET_KEY = "HospitalServiceDeskSecurityKey-ChangeThis"

ALGORITHM = "HS256"

TOKEN_EXPIRE_MINS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# =================================================
# CHECK DATABASE CONNECTION
# =================================================

print(db.list_collection_names())


# =================================================
# REQUEST SCHEMA
# =================================================

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
    id: str
    requestId: str


# =================================================
# USER SCHEMA
# =================================================

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    department: str
    password: str
    status: str = "active"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department: str
    status: str


# =================================================
# TOKEN SCHEMA
# =================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =================================================
# REQUEST HELPER
# =================================================

def request_helper(request):

    return {
        "id": str(request["_id"]),
        "requestId": request["requestId"],
        "title": request["title"],
        "description": request["description"],
        "department": request["department"],
        "category": request["category"],
        "priority": request["priority"],
        "status": request["status"],
        "raisedBy": request["raisedBy"],
        "assignedTo": request.get("assignedTo")
    }


# =================================================
# USER HELPER
# =================================================

def user_helper(user):

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department": user["department"],
        "status": user["status"]
    }


# =================================================
# CREATE JWT
# =================================================

def create_token(username: str, role: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINS
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =================================================
# GET CURRENT USER
# =================================================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if username is None or role is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = users_collection.find_one({
        "email": username
    })

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return user


# =================================================
# ROLE CHECK
# =================================================

def require_roles(*allowed_roles):

    def check_role(
        current_user=Depends(get_current_user)
    ):

        if current_user["role"] not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return check_role


# =================================================
# USER API
# =================================================


# CREATE USER

@app.post(
    "/users",
    status_code=201,
    response_model=UserResponse
)
def create_user(user: UserCreate):

    queried_user = users_collection.find_one({
        "email": user.email
    })

    if queried_user:

        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    hashed_pwd = password_hash.hash(
        user.password
    )

    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pwd,
        "role": user.role,
        "department": user.department,
        "status": user.status
    }

    result = users_collection.insert_one(user_data)

    new_user = users_collection.find_one({
        "_id": result.inserted_id
    })

    return user_helper(new_user)


# =================================================
# LOGIN
# =================================================

@app.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = users_collection.find_one({
        "email": form_data.username
    })

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        form_data.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(
        user["email"],
        user["role"]
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =================================================
# REQUEST APIs
# =================================================


# CREATE REQUEST
# All roles can create requests

@app.post(
    "/requests",
    status_code=201,
    response_model=RequestResponse
)
def request_create(
    payload: RequestCreate,
    current_user=Depends(
        require_roles(
            "Department Staff",
            "Support Engineer",
            "Team Lead",
            "Admin"
        )
    )
):

    request_dict = payload.model_dump()

    count = requests_collection.count_documents({})

    request_dict["requestId"] = f"REQ{count + 1:03d}"

    result = requests_collection.insert_one(
        request_dict
    )

    new_request = requests_collection.find_one({
        "_id": result.inserted_id
    })

    return request_helper(new_request)


# =================================================
# READ ALL REQUESTS
# All roles can read requests
# =================================================

@app.get(
    "/requests",
    response_model=list[RequestResponse]
)
def request_read_all(
    current_user=Depends(
        require_roles(
            "Department Staff",
            "Support Engineer",
            "Team Lead",
            "Admin"
        )
    )
):

    requests_result = requests_collection.find()

    requests = [
        request_helper(request)
        for request in requests_result
    ]

    return requests


# =================================================
# READ REQUEST BY ID
# All roles can read requests
# =================================================

@app.get(
    "/requests/{id}",
    response_model=RequestResponse
)
def request_read_by_id(
    id: str,
    current_user=Depends(
        require_roles(
            "Department Staff",
            "Support Engineer",
            "Team Lead",
            "Admin"
        )
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid request ID format"
        )

    request_result = requests_collection.find_one({
        "_id": ObjectId(id)
    })

    if not request_result:

        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return request_helper(request_result)


# =================================================
# UPDATE REQUEST
# Support Engineer, Team Lead and Admin
# =================================================

@app.put(
    "/requests/{id}",
    response_model=RequestResponse
)
def request_update(
    id: str,
    payload: RequestCreate,
    current_user=Depends(
        require_roles(
            "Support Engineer",
            "Team Lead",
            "Admin"
        )
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid request ID format"
        )

    result = requests_collection.update_one(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": payload.model_dump()
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    new_request = requests_collection.find_one({
        "_id": ObjectId(id)
    })

    return request_helper(new_request)


# =================================================
# DELETE REQUEST
# Only Admin
# =================================================

@app.delete("/requests/{id}")
def request_delete(
    id: str,
    current_user=Depends(
        require_roles("Admin")
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid request ID format"
        )

    result = requests_collection.delete_one({
        "_id": ObjectId(id)
    })

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return {
        "message": "request deleted successfully"
    }