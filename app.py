from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from transformers import AutoProcessor, AutoModelForVision2Seq
import torch
from PIL import Image
import io
import base64

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load model and processor
model_name = "microsoft/git-base-coco"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForVision2Seq.from_pretrained(model_name)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VisionQA Assistant</title>
        <link rel="stylesheet" type="text/css" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>VisionQA Assistant</h1>
            <p>Upload an image and ask a question about it</p>
            <form id="upload-form">
                <input type="file" id="image-upload" accept="image/*" required>
                <textarea id="question" placeholder="Ask a question about the image..." required></textarea>
                <button type="submit">Get Answer</button>
            </form>
            <div id="loading" style="display: none;">Processing...</div>
            <div id="result-container">
                <div id="image-preview"></div>
                <div id="answer"></div>
            </div>
        </div>
        <script src="/static/script.js"></script>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    # Read and process image
    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data))
    
    # Convert image to base64 for preview
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # Process with model
    inputs = processor(images=img, text=question, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50)
    
    answer = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    
    return {
        "image": f"data:image/jpeg;base64,{img_str}",
        "answer": answer
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
