import os
import csv
import io
from azure.storage.blob import BlobServiceClient, ContentSettings
from typing import Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_csv_to_blob(csv_file_path: str, folder_name: str = "ASR Testing Dump", 
                      blob_filename: Optional[str] = None, 
                      add_timestamp: bool = False) -> str:
    """
    Uploads a CSV file to Azure Blob Storage in a specified folder.
    
    Args:
        csv_file_path (str): Path to the CSV file to upload
        folder_name (str): Folder name in the blob container (default: "ASR Testing Dump")
        blob_filename (str, optional): Custom filename for the blob. If None, uses original filename
        add_timestamp (bool): Whether to add timestamp to filename (default: False)
    
    Returns:
        str: The URL of the uploaded blob
    """
    # Azure Storage Configuration
    account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', 'sarvamweb')
    container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'whatsappmedia')
    account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
    
    if not account_key:
        raise ValueError("AZURE_STORAGE_ACCOUNT_KEY environment variable not set")
    
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    try:
        # Check if file exists
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file does not exist: {csv_file_path}")
        
        # Validate it's a CSV file
        if not csv_file_path.lower().endswith('.csv'):
            raise ValueError("File must have .csv extension")
        
        # Get filename
        if blob_filename is None:
            blob_filename = os.path.basename(csv_file_path)
        
        # Add timestamp if requested
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(blob_filename)
            blob_filename = f"{name}_{timestamp}{ext}"
        
        # Construct blob path with folder
        blob_path = f"{folder_name}/{blob_filename}"
        
        # Initialize Azure clients
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        
        # Read and upload CSV file
        logger.info(f"Uploading {csv_file_path} to {blob_path}")
        
        with open(csv_file_path, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type="text/csv")
            )
        
        # Generate URL
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_path}"
        
        logger.info(f"Upload successful! File uploaded to: {blob_path}")
        logger.info(f"URL: {url}")
        
        return url
        
    except Exception as e:
        logger.error(f"Error uploading CSV file: {e}")
        raise


def upload_csv_data_to_blob(csv_data: str, filename: str, 
                           folder_name: str = "ASR Testing Dump", 
                           add_timestamp: bool = False) -> str:
    """
    Uploads CSV data as string to Azure Blob Storage.
    
    Args:
        csv_data (str): CSV data as string
        filename (str): Filename for the CSV (should include .csv extension)
        folder_name (str): Folder name in the blob container (default: "ASR Testing Dump")
        add_timestamp (bool): Whether to add timestamp to filename (default: False)
    
    Returns:
        str: The URL of the uploaded blob
    """
    # Azure Storage Configuration
    account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', 'sarvamweb')
    container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'whatsappmedia')
    account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
    
    if not account_key:
        raise ValueError("AZURE_STORAGE_ACCOUNT_KEY environment variable not set")
    
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    
    try:
        # Ensure filename has .csv extension
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        # Add timestamp if requested
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
        
        # Construct blob path with folder
        blob_path = f"{folder_name}/{filename}"
        
        # Initialize Azure clients
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        
        # Upload CSV data
        logger.info(f"Uploading CSV data to {blob_path}")
        
        blob_client.upload_blob(
            csv_data,
            overwrite=True,
            content_settings=ContentSettings(content_type="text/csv")
        )
        
        # Generate URL
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_path}"
        
        logger.info(f"Upload successful! CSV data uploaded to: {blob_path}")
        logger.info(f"URL: {url}")
        
        return url
        
    except Exception as e:
        logger.error(f"Error uploading CSV data: {e}")
        raise


# ASR Testing specific functions
def upload_asr_test_results(test_results: list, user_email: str, language: str, session_id: str) -> str:
    """
    Upload ASR test results to Azure Blob Storage.
    
    Args:
        test_results (list): List of test result dictionaries
        user_email (str): User's email address
        language (str): Test language
        session_id (str): Session identifier
    
    Returns:
        str: URL of uploaded CSV file
    """
    try:
        # Create CSV data manually
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['user_email', 'language', 'session_id', 'crop_name', 'attempt_number', 'transcript', 'keyword_detected', 'timestamp', 'upload_timestamp'])
        
        # Write data
        upload_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for result in test_results:
            writer.writerow([
                user_email,
                language,
                session_id,
                result.get('crop_name', ''),
                result.get('attempt_number', ''),
                result.get('transcript', ''),
                result.get('keyword_detected', ''),
                result.get('timestamp', ''),
                upload_timestamp
            ])
        
        csv_data = output.getvalue()
        output.close()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"asr_test_results_{user_email}_{language}_{timestamp}.csv"
        
        # Upload to Azure
        url = upload_csv_data_to_blob(
            csv_data=csv_data,
            filename=filename,
            folder_name="ASR Testing Dump",
            add_timestamp=False  # We already added timestamp to filename
        )
        
        logger.info(f"ASR test results uploaded successfully: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Error uploading ASR test results: {e}")
        raise

