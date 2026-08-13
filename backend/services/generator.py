import asyncio
import logging

from sqlmodel import Session , select
from database import engine 
from models import Job , Thumbnail 
from services.gemini_service import thumbnail_service
from services.imagekit_service import upload_file


logger=logging.getLogger(__name__)

STYLES={
    "bold_dramatic":(
        "A bold and dramatic style with high contrast, deep shadows, and vibrant colors. "
    ),
    "bright_colorful":(
        "A bright and colorful style with vivid colors, high saturation, and a cheerful atmosphere. "
    ),
    "minimalist":(
        "A minimalist style with clean lines, simple shapes, and a focus on negative space. "
    ),
}


STYLE_ORDER = ["bold_dramatic", "bright_colorful", "minimalist"]

async def generate_single_thumbnail(thumbnail_id:str,prompt:str,headshot_url:str):
    #DB mark -> Generating 
    with Session(engine) as session:
        thumb = session.get(Thumbnail,thumbnail_id)
        thumb.status = "generating"
        style_name=thumb.style_name
        session.commit()
    
    style_prompt = STYLES[style_name]
    #AI call 
    try:
        image_byte = thumbnail_service(prompt,style_prompt,headshot_url)
        with Session(engine) as session:
            thumb = session.get(Thumbnail , thumbnail_id)
            job_id = thumb.job_id
            job = session.get(Job , job_id)
    
        #Upload the image 
        
        url = upload_file(
            file_bytes=image_byte,
            file_name=f"{thumbnail_id}.png",
            folder_path=f"thumbnails/{job_id}/"
        )
    # DB call save the url  + mark uploaded 
        with Session(engine) as session:
            thumb = session.get(Thumbnail , thumbnail_id)
            thumb.imagekit_url = url
            thumb.status="updated"
            session.add(thumb)
            session.commit()
        logger.info(f"Thumbnail { thumbnail_id } generated and uploaded successfully .")
    
    except Exception as e:
        logger.error(f"Error generating thumbnail  { thumbnail_id }: {e}")
        with Session(engine) as session:
            thumb = thumb.get(Thumbnail,thumbnail_id)
            thumb.status="error"
            thumb.error_message = str(e)[:500]
            session.add(thumb)
            session.commit()
            
async def process_job(job_id:str):
    # mark job as processing
    # find all thumbnails for the job 
    # Start one worker  for each thumbnail 
    # wait with all workers to finish 
    # mark job as  coompleted/failed
    with Session(engine) as session:
        job = session.get(Job,job_id)
        job.status = "processing"
        prompt = job.prompt
        headshot_url =job.headshot_url
        session.add(job)
        session.commit()
        
        thumbnails = session.exec(
            select(Thumbnail).where(Thumbnail.job_id == job_id)
        )
        thumbnails_ids = [t.id for t in thumbnails]
        
        tasks = [
            generate_single_thumbnail(tid , prompt , headshot_url)
            for tid in thumbnails_ids
        ]
        await asyncio.gather(*tasks,return_exceptions=True)
        
        with Session(engine) as session:
            thumbnails = session.exec(
                select(Thumbnail).where(Thumbnial.job_id == job_id)
            ).all()