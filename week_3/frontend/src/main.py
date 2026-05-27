from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

app.mount(
    "/static",
    StaticFiles(directory="src/static"),
    name="static"
)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={"backend_url": BACKEND_URL}
    )
