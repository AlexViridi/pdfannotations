#app.py
import os
import uuid
from starlette.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile
from loguru import logger


# from flask import Flask, request, jsonify

# app = Flask(__name__)
# initialize the Fast API Application.
app = FastAPI(debug=True)


#Example data
jobs = [{"id": 0, "documents": ["file1", "file2", "file3"], "searchstrings": ["text1", "text2", "text3"]}, 
{"id": 1, "documents": ["file4", "file5", "file6"], "searchstrings": ["text4", "text5", "text6"]}, 
{"id": 2, "documents": ["file7", "file8", "file9"], "searchstrings": ["text7", "text8", "text9"]}]


def _find_next_id():
    return max(job["id"] for job in jobs) + 1

@app.post("/embedd_documents")
async def upload_documents(files: List[UploadFile] = File(...), aa_or_openai: str = "openai", token: Optional[str] = None) -> JSONResponse:
    """Uploads multiple documents to the backend.
    Args:
        files (List[UploadFile], optional): Uploaded files. Defaults to File(...).
    Returns:
        JSONResponse: The response as JSON.
    """
    tmp_dir = create_tmp_folder()

    file_names = []

    for file in files:
        file_name = file.filename
        file_names.append(file_name)

        # Save the file to the temporary folder
        if tmp_dir is None or not os.path.exists(tmp_dir):
            raise ValueError("Please provide a temporary folder to save the files.")

        if file_name is None:
            raise ValueError("Please provide a file to save.")

        with open(os.path.join(tmp_dir, file_name), "wb") as f:
            f.write(await file.read())

    embedd_documents_wrapper(folder_name=tmp_dir, aa_or_openai=aa_or_openai, token=token)
    return JSONResponse(content={"message": "Files received and saved.", "filenames": file_names})

# @app.get("/annotationsjobs")
# def get_annotationsjobs():
#     return jsonify(jobs)

# @app.post("/annotationsjobs")
# def create_job():
#     if request.is_json:
#         job = request.get_json()
#         job["id"] = _find_next_id()
#         jobs.append(job)
#         return job, 201
#     return {"error": "Request must be JSON"}, 415


# @app.get("/annotationsjobs/<job_id>")
# def get_annotationjob(job_id):
#     return jobs[int(job_id)]

# @app.get("/annotationsjobs/<job_id>/documents")
# def get_documents(job_id):
#     if "documents" in jobs[int(job_id)]:
#         docsarray = jobs[int(job_id)]["documents"]
#         return docsarray
#     return {"error": "No documents array found."}

# @app.get("/annotationsjobs/<job_id>/documents/<doc_id>")
# def get_document(job_id, doc_id):
#     return jobs[int(job_id)].documents[int(doc_id)]
