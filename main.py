from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def root():
    return {"message": "Hello World"}

# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
#     with open(file_path, "wb") as f:
#         f.write(await file.read())
#     return JSONResponse(content={"filename": file.filename})