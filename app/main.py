from fastapi import FastAPI
from app.api.v1.health import router as health_router
from app.api.v1.action import router as action_router

app = FastAPI()
app.include_router(health_router)
app.include_router(action_router)

# TODO: Add more routers and startup logic

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 