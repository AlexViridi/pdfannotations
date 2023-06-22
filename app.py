#app.py
import os
import uuid
from starlette.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Path
from loguru import logger
from typing import List, Optional, Annotated
from pydantic import BaseModel, ValidationError, validator
from enum import IntEnum
from annoclasses import StatusEnum, Documentdetails, Annotationjob
from anno import *

# initialize the Fast API Application.
app = FastAPI(debug=True)


def _find_next_id():
    return max(job["id"] for job in jobs) + 1

def create_tmp_folder(job_id) -> str:
    """Creates a temporary folder for files to store.
    Returns:
        str: The directory name.
    """
    # Create a temporary folder to save the files
    #tmp_dir = f"tmp_{str(uuid.uuid4())}"
    tmp_dir = f"tmp_{str(job_id)}"
    os.makedirs(tmp_dir)
    logger.info(f"Created new folder {tmp_dir}.")
    return tmp_dir

#Temporarily:
jobs = []

@app.post("/annotationjobs", status_code=201)
async def create_annotationjob(job: Annotationjob) -> JSONResponse:
    """Creates an annotation job.
    Args:
        -
    Request-Body:
        at least one aa explanation to search for    
    Returns:
        JSONResponse: The response as JSON.
    """   
    job.id = uuid.uuid4()
    jobs.append(job)
    return job

@app.post("/annotationjobs/{job_id}/documents", status_code=201)
async def upload_documents(job_id: Annotated[uuid.UUID, Path(title="The ID of the corresponding job for the documents")], files: List[UploadFile] = File(...)) -> JSONResponse:
    """Uploads multiple documents to the backend and assigns them to the given job ID.
    Args:
        job_id <Path_Parameter>: (uuid.UUID,  The ID of the corresponding job for the documents)
        files (List[UploadFile], optional): Uploaded files. Defaults to File(...).
    Returns:
        JSONResponse: The response as JSON.
    """
    tmp_dir = create_tmp_folder(job_id)

    file_names = []
    jobindex = [i for i in range(len(jobs)) if jobs[i].id == job_id]
    if jobindex is not None:
        job = jobs[jobindex[0]]
        job.documentdetails = []
    for file in files:
        file_name = file.filename
        file_names.append(file_name)

        # Save the file to the temporary folder
        if tmp_dir is None or not os.path.exists(tmp_dir):
            raise ValueError("Please provide a temporary folder to save the files.")

        if file_name is None:
            raise ValueError("Please provide a file to save.")

        #with open(os.path.join(tmp_dir, file_name), "wb") as f:
        details = Documentdetails(
            id=uuid.uuid4(),
            originalname=file_name,
            newname=os.path.splitext(file_name)[0] + '_anno' + os.path.splitext(file_name)[1],
            status=StatusEnum.new,
            errordetails=""
        )
        job.documentdetails.append(details)
        logger.info(f"Document details {details.json()}")
        with open(os.path.join(tmp_dir, details.newname), "wb") as f:
            f.write(await file.read())
    jobs[jobindex[0]] = job
    for doc in job.documentdetails:
        doc.status = StatusEnum.working
        annotated = await search_and_annotate_allpages(os.path.join(tmp_dir, doc.newname), job.explanations)
        doc.status = annotated
        
    #To-Do: Enqueue documents for processing
    #embedd_documents_wrapper(folder_name=tmp_dir, aa_or_openai=aa_or_openai, token=token)
    return JSONResponse(content={"message": "Files received and saved.", "filenames": file_names})

# @app.get("/annotationsjobs")
# def get_annotationsjobs():
#     return jsonify(jobs)

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
