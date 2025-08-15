from crewai.tools import BaseTool, tool
from typing import Type
from pydantic import BaseModel, Field

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
CONTAINER_NAME = "resumes"
METADATA_KEY = "uuid"

def get_sas_token(account_name: str, account_key: str, blob_name: str, expiry_hours: int = 1) -> str:
    """
    Generate a read-only SAS token for the specified blob, valid for expiry_hours.
    """
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now() + timedelta(hours=expiry_hours)
    )
    return sas_token

@tool("Generate download link tool")
def download_link_generator( METADATA_VALUE: str) -> str:
    """ Used to Generate Download link for Resume of candidate using Candidate unique identifier"""
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    account_name = blob_service_client.account_name
    account_key = blob_service_client.credential.account_key
    if not account_key:
        raise ValueError("Account key not found in client credential. Ensure you're using a connection string with account key.")

    blobs = container_client.list_blobs(include=["metadata"])
    download_urls = []

    for blob in blobs:
        meta = blob.metadata or {}
        if meta.get(METADATA_KEY) == METADATA_VALUE and blob.name.lower().endswith('.pdf'):
            sas_token = get_sas_token(account_name, account_key, blob.name, 2)
            blob_client = container_client.get_blob_client(blob.name)
            url_with_sas = f"{blob_client.url}?{sas_token}"
            download_urls.append(url_with_sas)
            print(f"Download URL for {blob.name}: {url_with_sas}")

    return download_urls