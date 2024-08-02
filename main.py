from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image  # Import Pillow

import subprocess
import os
import pymupdf  # PyMuPDF
import boto3
import concurrent.futures

app = FastAPI()
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabae_storage_access_key_id = os.getenv("SUPABASE_STORAGE_ACCESS_KEY_ID")
supabae_storage_secret_acesss_key = os.getenv("SUPABASE_STORAGE_SECRET_ACCESS_KEY")
                                           
s3_client = boto3.client(
    's3',
    region_name='ap-southeast-1',
    endpoint_url='https://jzwwqvvsgdyremmxzfom.supabase.co/storage/v1/s3',
    aws_access_key_id=supabae_storage_access_key_id,
    aws_secret_access_key=supabae_storage_secret_acesss_key # This corresponds to `forcePathStyle: true`
)

@app.get("/")
def root():
    return {"message": "Hello World"}

UPLOAD_DIRECTORY = "./uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    
@app.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, 
                      file_id: str = Form(...),
                      user_id: str = Form(...), 
                      file: UploadFile = File(...)):
    # Create a user-specific directory
    user_directory = os.path.join(UPLOAD_DIRECTORY, user_id)
    os.makedirs(user_directory, exist_ok=True)
    
    filename = file.filename.split(".")[0]
    
    # Create a directory for the file without the extension
    file_directory = os.path.join(user_directory, file_id)
    os.makedirs(file_directory, exist_ok=True)

    # Save the uploaded file temporarily
    temp_pdf_path = os.path.join(file_directory, file.filename)
    with open(temp_pdf_path, "wb") as f:
        f.write(await file.read())
        
    # Convert the PDF to images
    doc = pymupdf.open(temp_pdf_path)
    zoom = 4
    mat = pymupdf.Matrix(zoom, zoom)
    count = 0
    images_path = []
    for p in doc:
        count += 1
    for i in range(count):
        val = f"{file_directory}/{filename}_{i+1}.png"
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        pix.save(val)
        images_path.append(val)
    
    background_tasks.add_task(start_omr_process, file_directory, images_path)
    return JSONResponse(content={"message": "PDF converting in the background"})

def start_omr_process(output_path: str, images_path: [str]):
    print("Starting OMR process...")
    for path in images_path:
        subprocess.run(["oemer", "-o", output_path, path], check=True)
    
    files = get_musicxml_files(output_path)
    if len(files) == 0:
        print("No .musicxml files found.")
        return
    
    for file in files:
        path_on_supastorage = f"{file.relative_to(Path(UPLOAD_DIRECTORY))}"
        upload_file_to_supabase(file, path_on_supastorage)
        print(path_on_supastorage)
        

def upload_file_to_supabase(file_path: str, path_on_supastorage: str):
    bucket_name = 'sheets'
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    if bucket_name not in buckets:
            print(f"Bucket '{bucket_name}' does not exist. Creating bucket...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")   
        
    s3_client.upload_file(file_path, bucket_name, path_on_supastorage)
    

def get_musicxml_files(directory):
    # Create a Path object for the directory
    dir_path = Path(directory)
    # Use the glob method to get all .musicxml files
    files = list(dir_path.glob('*.musicxml'))
    return files
# To run the app, use: `uvicorn main:app --reload`