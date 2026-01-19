from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Persons API", description="In-memory persons service with MCP endpoint")

# In-memory storage
persons_db = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

#----

# GET: Search person
@app.get("/person/{person_id}")
def get_person(person_id: int):
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons_db[person_id]

# POST: Add person
@app.post("/person/{person_id}")
def add_person(person_id: int, firstName: str, lastName: str):
    persons_db[person_id] = {"firstName": firstName, "lastName": lastName}
    return {"message": f"Person {firstName} {lastName} added with ID {person_id}"}

# MCP endpoint
@app.get("/mcp")
def get_mcp():
    mcp_data = {
        "serviceName": "PersonsService",
        "description": "In-memory person storage service",
        "endpoints": [
            {
                "path": "/person/{person_id}",
                "method": "GET",
                "description": "Fetch a person by ID",
                "pathParameters": [{"name": "person_id", "type": "integer", "required": True}],
                "response": {
                    "type": "object",
                    "properties": {
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"}
                    }
                }
            },
            {
                "path": "/person/{person_id}",
                "method": "POST",
                "description": "Add a new person",
                "pathParameters": [{"name": "person_id", "type": "integer", "required": True}],
                "queryParameters": [
                    {"name": "firstName", "type": "string", "required": True},
                    {"name": "lastName", "type": "string", "required": True}
                ],
                "response": {"type": "object", "properties": {"message": {"type": "string"}}}
            }
        ]
    }
    return JSONResponse(content=mcp_data)
