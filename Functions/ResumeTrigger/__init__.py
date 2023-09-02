import logging
import tempfile
import azure.functions as func
from .main import boost_resume_to_json
from .file_check import is_pdf


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the resume file from the request
    try:
        req_body = req.files['resume']
        filename = req_body.filename
        if not is_pdf(filename):
            raise Exception
        file_content = req_body.read()
        logging.info(f'Received resume file: {filename}')
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Please upload a pdf resume file.", status_code=400)

    boost_passed, request_status, boosted_response = boost_resume_to_json(
        file_content)

    # Set CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    if not boost_passed:
        response = func.HttpResponse(
            boosted_response, status_code=request_status, headers=headers)
    else:
        response = func.HttpResponse(
            boosted_response,
            status_code=request_status,
            mimetype="application/json",
            headers=headers
        )

    return response
