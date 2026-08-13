import httpx
from google import genai
from backend.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_thumbnail(prompt: str, style_prompt: str, headshot_url: str) -> bytes:
    """
    Generate a thumbnail using the Gemini API.
    Fetches the headshot, passes it to the model, and returns raw PNG/JPEG bytes.
    """
    
    full_prompt = (
        f"{style_prompt}\n\n"
        f"User request: {prompt}.\n\n"
        "Important: The generated thumbnail MUST prominently feature the person "
        "shown in the headshot image. Keep their face clearly visible, recognizable and likeness accurate. "
        "The thumbnail should be visually appealing, clear, and suitable for use as a YouTube thumbnail."
    )

    # Optional but recommended: Fetch the image bytes yourself to ensure it passes cleanly
    async with httpx.AsyncClient() as http_client:
        image_response = await http_client.get(headshot_url)
        image_response.raise_for_status()
        headshot_bytes = image_response.content

    # Use client.aio for async calls!
    interaction = await client.aio.interactions.create(
        model="gemini-3.6-flash",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    # Pass the raw image bytes to ensure the API receives it correctly
                    {"type": "input_image", "data": headshot_bytes} 
                ]
            }
        ],
        modalities=["text", "image"], # Tells the model we want an image back
    )
    
    # Extract the generated image bytes (assuming the model outputs an image in the first response)
    # The exact attribute name depends on the SDK version, but it generally lives in an images array
    if not interaction.output_images:
        raise ValueError("The model did not return an image.")
        
    return interaction.output_images[0].image_bytes 