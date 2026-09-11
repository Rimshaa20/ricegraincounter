"""
Rice Grain Counter - Backend API

FastAPI server that accepts an image upload, processes it with OpenCV
to detect and count rice grains, and returns the result + annotated image.

Run with:
    cd backend
    pip install -r requirements.txt
    python main.py

The server starts at http://localhost:8000
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from rice_counter import count_rice_grains, RiceConfig

app = FastAPI(title="Rice Grain Counter API")

# Allow requests from the Vite dev server (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ricegraincounter.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Max upload size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Rice Grain Counter API is running"}


@app.post("/count-rice")
async def count_rice(file: UploadFile = File(...)):
    """
    Accept an uploaded image, detect rice grains using OpenCV,
    and return the count + annotated image.
    """
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. "
                   f"Supported formats: JPG, JPEG, PNG"
        )

    # Read file bytes and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(contents) / (1024*1024):.1f} MB). "
                   f"Maximum size is 10 MB."
        )
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        cfg = RiceConfig()
        result = count_rice_grains(contents, config=cfg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

    # Encode annotated image as base64 so it can travel in JSON
    import base64
    annotated_b64 = base64.b64encode(result["annotated_image_bytes"]).decode("utf-8")

    return {
        "total_count": result["total_count"],
        "message": result["message"],
        "annotated_image": annotated_b64,
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Rice Grain Counter API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
