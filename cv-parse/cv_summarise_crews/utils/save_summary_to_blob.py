import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
load_dotenv()
def save_to_blob():
    try:
        connection_string = os.getenv("CONNECTION_STRING")
        container_name = "summaries"
        
        for filename in os.listdir("summaries"):
            if filename.endswith(".txt"):
                file_path = os.path.join("summaries", filename)
                blob_name = f"summaries/{filename}"
                
                # Create a BlobServiceClient
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                container_client = blob_service_client.get_container_client(container_name)
                
                # Upload the file to Azure Blob Storage
                with open(file_path, "rb") as data:
                    container_client.upload_blob(name=blob_name, data=data, overwrite=True)
                    print(f"Uploaded {file_path} to {blob_name} in Azure Blob Storage.")
    except Exception as e:
        print(f"An error occurred while uploading files to Azure Blob Storage: {e}")
