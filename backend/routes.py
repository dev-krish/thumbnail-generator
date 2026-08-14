import os
import logging

from fastapi import APIRouter , Depends , HTTPSException , UploadFile , File 
from fastapi.responses import  StreamingResponse
from pydantic import Session , select
from database import get_session

from database  import get_session
from models import Job , Thumbnail

from backend.services.generator import process_job , STYLE_ORDER 
from services.imagekit_service import upload_file , get_variants

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# request response schemas

class CreateJobRequest(BaseModel):
    prompt:str
    num_thumbnails:int
    headshot_url:str
    
class CreateJobResponse(BaseModel):
    job_id:str

class ThumbnailResponse(BaseModel):
    id:int
    style_name:str
    