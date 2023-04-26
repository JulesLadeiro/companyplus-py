# System imports
# Libs imports
from fastapi import FastAPI
# Local imports
from routers import user
from internals import auth
from db.database import engine, Base

Base.metadata.create_all(bind=engine)


app = FastAPI()


custom_responses = {
    200: {"description": "OK"},
    201: {"description": "Created"},
    204: {"description": "No content"},
    400: {"description": "Bad request"},
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    404: {"description": "Not found"},
}

app.include_router(user.router, tags=["users"], responses=custom_responses)
app.include_router(auth.router, tags=[
                   "authentication"], responses=custom_responses)
