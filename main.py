import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.ai_suggestions.ai_suggestions_route import router as suggestion_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(suggestion_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.1.0", port=8085, reload=True)

