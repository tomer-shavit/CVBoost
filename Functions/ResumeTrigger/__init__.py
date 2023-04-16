import logging
import tempfile
import azure.functions as func
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

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        boosted_data_json = boost_resume_to_json(tmp.name)

    # Set CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    # Create the response with the CORS headers
    response = func.HttpResponse(
        boosted_data_json,
        status_code=200,
        mimetype="application/json",
        headers=headers
    )

    return response
