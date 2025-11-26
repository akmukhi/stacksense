from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="StackSense API",
    description="Hello World API for StackSense",
    version="1.0.0"
)

# Configure CORS to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}

@app.get("/api/hello")
async def hello():
    return {
        "message": "Hello World!",
        "status": "success",
        "framework": "FastAPI"
    }