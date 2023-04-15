# System imports
# Libs imports
from fastapi import FastAPI, status
# Local imports
from routers import user
from internals import auth
from database import engine
from models import Base

Base.metadata.create_all(bind=engine)


app = FastAPI()


custom_responses = {
    404: {"description": "Not found"},
    400: {"description": "Bad request"},
    204: {"description": "No content"}
}

app.include_router(user.router, tags=["users"], responses=custom_responses)
app.include_router(auth.router, tags=[
                   "authentication"], responses=custom_responses)
