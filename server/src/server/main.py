import uvicorn
from fastapi import FastAPI

from server.api.v1.cv import cv_router
from server.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/")
async def health_check():
    return {"status": "Ok", "message": "Server is running!"}

app.include_router(cv_router, prefix="/api/v1")


def main():
    uvicorn.run(
        "server.main:app", 
        host=settings.app_host, 
        port=settings.app_port, 
        reload=settings.app_host == "0.0.0.0"
    )


if __name__ == "__main__":
    main()