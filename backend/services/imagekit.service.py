from imagekitio import ImageKit

from backend.config import IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT

imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY,
)

# Store URL endpoint for reuse
URL_ENDPOINT = IMAGEKIT_URL_ENDPOINT

def upload_file(file_bytes: bytes,file_name:str,folder:str,content_type:str = "image/png"):
    """Uploads a file to ImageKit and returns the CDN URL ."""
    result = imagekit.files.upload(
        file=(file_bytes,file_name,content_type),
        file_name=file_name,
        folder=folder,
        is_private_file=False,
        use_unique_file_name=True,
    )
    
    return result.url

def get_variants(base_url:str)-> dict:
    """Returns a dictionary of variant URLs for the given base URL."""
    variants = {
        "youtube": f"{base_url}?tr=w-1280,h-720,c-maitain_ratio ,fo-auto",
        "shorts": f"{base_url}?tr=w-1080,h-1920,c-maitain_ratio,fo-auto",
        "square": f"{base_url}?tr=w-1080,h-1080,c-maitain_ratio,fo-auto",
    }
    return variants