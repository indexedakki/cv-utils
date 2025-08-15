from azure.storage.blob import BlobServiceClient
import os

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

def download_from_blob():
    if not os.path.exists("summaries"):
        logger.info("Creating directory 'summaries'.")
        os.makedirs("summaries", exist_ok=True)
    # Set up the connection to Azure Blob Storage
    connection_string = os.getenv("CONNECTION_STRING")
    container_name = "summaries"
    
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    # Download all blobs in the container
    for blob in container_client.list_blobs():
        blob_name = blob.name
        file_path = os.path.join("summaries", os.path.basename(blob_name))
        
        with open(file_path, "wb") as file:
            data = container_client.download_blob(blob_name)
            file.write(data.readall())
            print(f"Downloaded {blob_name} to {file_path}.")
