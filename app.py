#app.py
import os
import uuid
from starlette.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Path
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
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

@app.get(" ")
def get_jobs() -> JSONResponse:
    """Returns json list of current jobs.
    Args:
        - 
    Returns:
        JSONResponse: The job list as JSON.
    """   
    json_compatible_item_data = jsonable_encoder(jobs)
    return JSONResponse(json_compatible_item_data)

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
        
        with open(os.path.join(tmp_dir, file_name), "wb") as f:
            f.write(await file.read())

        #Create document details
        details = Documentdetails(
            id=uuid.uuid4(),
            originalname=file_name,
            newname=os.path.splitext(file_name)[0] + '_anno' + os.path.splitext(file_name)[1],
            status=StatusEnum.new,
            errordetails=""
        )
        job.documentdetails.append(details)
        logger.info(f"Document details {details.json()}")
    jobs[jobindex[0]] = job
    searchresult = search_and_annotate_allpages(job, tmp_dir)      
    #To-Do: Enqueue documents for processing
    #To-Do: Bei Response-Code 201 muss die Antwort leer sein 
    return JSONResponse(content={"message": "Files received and saved.", "filenames": file_names})

@app.get("/annotationjobs/{job_id}/documents/{document_id}", response_class=FileResponse, status_code=200)
def get_document(job_id: Annotated[uuid.UUID, Path(title="The ID of the job of the documents")], 
document_id: Annotated[uuid.UUID, Path(title="The ID of the document to be retrieved")]):
    """Sends a file to caller.
    Args:
        job_id <Path_Parameter>: (uuid.UUID,  The ID of the job of the documents)
        document_id <Path_Parameter>: (uuid.UUID,  The ID of the document to be retrieved)
    Returns:
        File
    """
    #jobindex = next((x for x in jobs if x.id == job_id), None) #Find list element by value of class value
    jobindex = next((x for x in range(len(jobs)) if jobs[x].id == job_id), None) #Find index of list element by value of class value
    if jobindex is not None:
        currentjob = jobs[jobindex]
        documentindex = next((x for x in range(len(currentjob.documentdetails)) if currentjob.documentdetails[x].id == document_id), None) #Find list element by value of class value
        if documentindex is not None:
                return os.path.join(f"tmp_{str(job_id)}", currentjob.documentdetails[documentindex].newname)
        raise ValueError("Document not found.")
    raise ValueError("Job not found.")
