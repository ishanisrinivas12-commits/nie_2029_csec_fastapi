from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()
@app.get("/")
def home():
    return{"message":"enterprise it service desk"}

db={1:{"id":1,
       "title":"computer not on",
       "description":"power button not working",
       "category":"hardware",
       "status":"new"},
    2:{"id":2,
       "title":"internet not working",
       "description":"wifi problem",
       "category":"hardware",
       "status":"new"}
}
#schema
class TicketCreate(BaseModel):
    title:str
    description:str
    category:str
    status:str
#inheritence
class TicketResponse(TicketCreate):
    id : int
#apis
@app.get("/tickets/{id}")
def ticket_read_id(id : int):
    if id not in db:
        raise HTTPException(status_code=404,detail="ticket not found")
    return db[id]
@app.post("/tickets",status_code=201,response_model=TicketResponse)
def ticket_create(ticket_payload:TicketCreate):
    new_id =max(db.keys(),default=0) +1
    db[new_id]={"id":new_id,**ticket_payload.model_dump()}
    return db[new_id]

@app.put("/tickets/{id}",response_model=TicketResponse)
def tickets_update(id: int,payload:TicketCreate):
    if id not in db:
        raise HTTPException(detail="ticket not found",status_code=404)
    db[id]={"id":id, **payload.model_dump()}
    return db[id]

@app.delete("/tickets/{id}")
def tickets_delete(id:int):
    if id not in db:
        raise HTTPException(detail="ticket not found",status_code=404)
    del db[id]
    return {"message":"ticket deleted succes"}
    
