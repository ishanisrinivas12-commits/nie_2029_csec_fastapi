from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from pymongo import MongoClient
from bson import ObjectId

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

app = FastAPI()

URL = "mongodb://127.0.0.1:27017"

client = MongoClient(URL)

db = client["hospital"]

requests_collection = db["requests"]
users_collection = db["users"]
departments_collection = db["departments"]
categories_collection = db["categories"]
config_collection = db["config"]

password_hash = PasswordHash.recommended()

SECRET_KEY = "HospitalServiceDeskSecurityKey-ChangeThis"

ALGORITHM = "HS256"

TOKEN_EXPIRE_MINS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


print(db.list_collection_names())
class RequestCreate(BaseModel):
    title: str
    description: str
    department: str
    category: str
    priority: str
    status: str = "New"
    assignedTo: str | None = None


class RequestResponse(BaseModel):
    id: str
    requestId: str
    title: str
    description: str
    department: str
    category: str
    priority: str
    status: str
    raisedBy: str
    assignedTo: str | None = None

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

class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: str
    name: str



class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: str
    name: str

class ConfigCreate(BaseModel):
    hospital_name: str
    auto_assign_enabled: bool
    request_statuses: list[str]
    priority_levels: list[str]


class ConfigResponse(BaseModel):
    id: str
    hospital_name: str
    auto_assign_enabled: bool
    request_statuses: list[str]
    priority_levels: list[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

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



def user_helper(user):

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department": user["department"],
        "status": user["status"]
    }




def department_helper(department):

    return {
        "id": str(department["_id"]),
        "name": department["name"]
    }



def category_helper(category):

    return {
        "id": str(category["_id"]),
        "name": category["name"]
    }



def config_helper(config):

    return {
        "id": str(config["_id"]),
        "hospital_name": config["hospital_name"],
        "auto_assign_enabled": config["auto_assign_enabled"],
        "request_statuses": config["request_statuses"],
        "priority_levels": config["priority_levels"]
    }



def create_token(email: str, role: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINS
    )

    payload = {
        "sub": email,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token




def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")
        role = payload.get("role")

        if email is None or role is None:

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
        "email": email
    })

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user




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

    result = users_collection.insert_one(
        user_data
    )

    new_user = users_collection.find_one({
        "_id": result.inserted_id
    })

    return user_helper(new_user)




@app.get(
    "/users",
    response_model=list[UserResponse]
)
def get_users(
    current_user=Depends(get_current_user)
):

    users = users_collection.find()

    return [
        user_helper(user)
        for user in users
    ]

@app.get(
    "/users/{id}",
    response_model=UserResponse
)
def get_user(
    id: str,
    current_user=Depends(get_current_user)
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )

    user = users_collection.find_one({
        "_id": ObjectId(id)
    })

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user_helper(user)



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

    # Automatically store who raised the request
    request_dict["raisedBy"] = current_user["email"]

    result = requests_collection.insert_one(
        request_dict
    )

    new_request = requests_collection.find_one({
        "_id": result.inserted_id
    })

    return request_helper(new_request)




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



@app.post(
    "/departments",
    status_code=201,
    response_model=DepartmentResponse
)
def create_department(
    department: DepartmentCreate,
    current_user=Depends(
        require_roles("Admin")
    )
):

    existing = departments_collection.find_one({
        "name": department.name
    })

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Department already exists"
        )

    result = departments_collection.insert_one(
        department.model_dump()
    )

    new_department = departments_collection.find_one({
        "_id": result.inserted_id
    })

    return department_helper(new_department)


@app.get(
    "/departments",
    response_model=list[DepartmentResponse]
)
def get_departments(
    current_user=Depends(get_current_user)
):

    departments = departments_collection.find()

    return [
        department_helper(department)
        for department in departments
    ]




@app.get(
    "/departments/{id}",
    response_model=DepartmentResponse
)
def get_department(
    id: str,
    current_user=Depends(get_current_user)
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid department ID"
        )

    department = departments_collection.find_one({
        "_id": ObjectId(id)
    })

    if not department:

        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department_helper(department)


# UPDATE DEPARTMENT
# Admin only

@app.put(
    "/departments/{id}",
    response_model=DepartmentResponse
)
def update_department(
    id: str,
    department: DepartmentCreate,
    current_user=Depends(
        require_roles("Admin")
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid department ID"
        )

    result = departments_collection.update_one(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": department.model_dump()
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    updated_department = departments_collection.find_one({
        "_id": ObjectId(id)
    })

    return department_helper(updated_department)


# DELETE DEPARTMENT
# Admin only

@app.delete("/departments/{id}")
def delete_department(
    id: str,
    current_user=Depends(
        require_roles("Admin")
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid department ID"
        )

    result = departments_collection.delete_one({
        "_id": ObjectId(id)
    })

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return {
        "message": "department deleted successfully"
    }


# =================================================
# CATEGORY APIs
# =================================================


# CREATE CATEGORY
# Admin only

@app.post(
    "/categories",
    status_code=201,
    response_model=CategoryResponse
)
def create_category(
    category: CategoryCreate,
    current_user=Depends(
        require_roles("Admin")
    )
):

    existing = categories_collection.find_one({
        "name": category.name
    })

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    result = categories_collection.insert_one(
        category.model_dump()
    )

    new_category = categories_collection.find_one({
        "_id": result.inserted_id
    })

    return category_helper(new_category)


# GET ALL CATEGORIES

@app.get(
    "/categories",
    response_model=list[CategoryResponse]
)
def get_categories(
    current_user=Depends(get_current_user)
):

    categories = categories_collection.find()

    return [
        category_helper(category)
        for category in categories
    ]


# GET CATEGORY BY ID

@app.get(
    "/categories/{id}",
    response_model=CategoryResponse
)
def get_category(
    id: str,
    current_user=Depends(get_current_user)
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid category ID"
        )

    category = categories_collection.find_one({
        "_id": ObjectId(id)
    })

    if not category:

        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category_helper(category)


# UPDATE CATEGORY
# Admin only

@app.put(
    "/categories/{id}",
    response_model=CategoryResponse
)
def update_category(
    id: str,
    category: CategoryCreate,
    current_user=Depends(
        require_roles("Admin")
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid category ID"
        )

    result = categories_collection.update_one(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": category.model_dump()
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    updated_category = categories_collection.find_one({
        "_id": ObjectId(id)
    })

    return category_helper(updated_category)


# DELETE CATEGORY
# Admin only

@app.delete("/categories/{id}")
def delete_category(
    id: str,
    current_user=Depends(
        require_roles("Admin")
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid category ID"
        )

    result = categories_collection.delete_one({
        "_id": ObjectId(id)
    })

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return {
        "message": "category deleted successfully"
    }


# =================================================
# CONFIG APIs
# =================================================


# CREATE CONFIG
# Admin only

@app.post(
    "/config",
    status_code=201,
    response_model=ConfigResponse
)
def create_config(
    config: ConfigCreate,
    current_user=Depends(
        require_roles("Admin")
    )
):

    existing = config_collection.find_one()

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Config already exists"
        )

    result = config_collection.insert_one(
        config.model_dump()
    )

    new_config = config_collection.find_one({
        "_id": result.inserted_id
    })

    return config_helper(new_config)


# GET CONFIG
# All logged-in users

@app.get(
    "/config",
    response_model=ConfigResponse
)
def get_config(
    current_user=Depends(get_current_user)
):

    config = config_collection.find_one()

    if not config:

        raise HTTPException(
            status_code=404,
            detail="Config not found"
        )

    return config_helper(config)


# UPDATE CONFIG
# Admin only

@app.put(
    "/config/{id}",
    response_model=ConfigResponse
)
def update_config(
    id: str,
    config: ConfigCreate,
    current_user=Depends(
        require_roles("Admin")
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid config ID"
        )

    result = config_collection.update_one(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": config.model_dump()
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Config not found"
        )

    updated_config = config_collection.find_one({
        "_id": ObjectId(id)
    })

    return config_helper(updated_config)