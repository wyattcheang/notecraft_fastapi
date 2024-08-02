from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import boto3

import subprocess
import os

import fitz  # PyMuPDF
import boto3

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


upload_file_to_supabase("twinkle.musicxml", "A/twinkle.musicxml")