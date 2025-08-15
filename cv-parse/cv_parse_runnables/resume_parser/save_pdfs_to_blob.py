import os
import uuid
from azure.storage.blob import BlobServiceClient

from logger_setup import setup_logger

LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

import uuid

async def save_to_blob_with_metadata(resume, file_uuid):
    conn_str = os.getenv("CONNECTION_STRING")
    container_name = "resumes"
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)    
    blob_name = f"{resume.filename}"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    blob_client.upload_blob(resume.file, 
                            overwrite=True, 
                                metadata={"uuid": file_uuid})
    
    logger.info(f"Uploaded {resume.filename} to blob storage with UUID {file_uuid}")
    return file_uuid