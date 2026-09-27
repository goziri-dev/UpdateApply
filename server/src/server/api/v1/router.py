from fastapi import APIRouter

from server.api.v1.cv import cv_router
from server.api.v1.job import job_router
from server.api.v1.resume import resume_router

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(cv_router)
api_v1.include_router(job_router)
api_v1.include_router(resume_router)
