import logging
import tempfile
import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from .main import boost_resume_to_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the resume file from the request
    try:
        req_body = req.files['resume']
        filename = req_body.filename
        file_content = req_body.read()
        logging.info(f'Received resume file: {filename}')
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Please upload a resume file.", status_code=400)

    # Save the resume file to Azure Blob Storage
    # connection_string = os.environ['AzureWebJobsStorage']
    # blob_service_client = BlobServiceClient.from_connection_string(
    #     connection_string)
    # container_name = 'resumes'
    # container_client = blob_service_client.get_container_client(container_name)
    # blob_client = container_client.get_blob_client(filename)
    # blob_client.upload_blob(file_content)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        boosted_data_json = boost_resume_to_json(tmp.name)

    return func.HttpResponse(boosted_data_json, mimetype='application/json')
