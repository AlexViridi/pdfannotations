#app.py
import os
import uuid
from uuid import UUID
from starlette.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Path, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger
from typing import List, Optional, Annotated
from pydantic import BaseModel, ValidationError, validator
from enum import IntEnum
from annoclasses import StatusEnum, Documentdetails, Annotationjob, JobStatusEnum
from anno import *
from datetime import datetime

# initialize the Fast API Application.
app = FastAPI(debug=True)


def _find_next_id():
    return max(job["id"] for job in jobs) + 1

def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

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

def delete_job_in_background(job_id):
    jobindex = next((x for x in range(len(jobs)) if jobs[x].id == job_id), None)
    if jobindex is not None:
        currentjob = jobs[jobindex]
        for document in currentjob.documentdetails:
            if os.path.isfile(os.path.join(f"tmp_{str(job_id)}", document.originalname)) and document.status in [StatusEnum.done_annotated, StatusEnum.done_not_annotated, StatusEnum.error]:
                try:
                    os.remove(os.path.join(f"tmp_{str(job_id)}", document.originalname))
                except:
                    logger.info("The file %s is still in use and can't be removed currently.", document.originalname)
                else:
                    if document.status == StatusEnum.done_annotated:
                        if os.path.isfile(os.path.join(f"tmp_{str(job_id)}", document.newname)):
                            try:
                                os.remove(os.path.join(f"tmp_{str(job_id)}", document.newname))
                            except:
                                logger.info("The file %s is still in use and can't be removed currently.", document.newname)
                        try:
                            os.rmdir(f"tmp_{str(job_id)}")
                        except:
                            logger.info("The directory %s can't be removed at the moment. Maybe it's not empty.", f"tmp_{str(job_id)}")
                        else:
                            jobs.pop(jobindex)
                        

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
    job.status = JobStatusEnum.empty
    jobs.append(job)
    return job

@app.get("/annotationjobs")
def get_jobs() -> JSONResponse:
    """Returns json list of current jobs.
    Args:
        - 
    Returns:
        JSONResponse: The job list as JSON.
    """   
    json_compatible_item_data = jsonable_encoder(jobs)
    return JSONResponse(json_compatible_item_data) 

@app.delete("/annotationjobs/{job_id}", status_code=202)
async def delete_job(job_id: Annotated[uuid.UUID, Path(title="The job ID to be deleted")], background_tasks: BackgroundTasks):
    """Removes a given job.
    Args:
        job_id <Path_Parameter>: (uuid.UUID,  The job ID to be deleted")
    Returns:
        Status 202
    """
    if is_valid_uuid(job_id):
        jobindex = next((x for x in range(len(jobs)) if jobs[x].id == job_id), None)
        if jobindex is not None:
            background_tasks.add_task(delete_job_in_background, job_id)
        else:
            raise ValueError("Please provide a valid job id.")
    raise ValueError("Job id isn't a valid UUID")
        
    

@app.get("/annotationjobs/{job_id}/documents")
def get_documents_for_job(job_id: Annotated[uuid.UUID, Path(title="The ID of the corresponding job for the documents")]) -> JSONResponse:
    """Gets document information for given job.
    Args:
        job_id <Path_Parameter>: (uuid.UUID,  The ID of the corresponding job for the documents")
    Returns:
        JSONResponse: The response as JSON.
    """
    if is_valid_uuid(job_id):
        jobindex = next((x for x in range(len(jobs)) if jobs[x].id == job_id), None) #Find index of list element by value of class value
        if jobindex is not None:
            currentjob = jobs[jobindex]
            json_compatible_item_data = jsonable_encoder(currentjob.documentdetails)
            return JSONResponse(json_compatible_item_data)
        else:
            return JSONResponse('"message": "the job does not have any documents."')
    raise ValueError("Please provide a valid UUID for Job ID")

@app.post("/annotationjobs/{job_id}/documents", status_code=201)
async def upload_documents(job_id: Annotated[uuid.UUID, Path(title="The ID of the corresponding job for the documents")],
                           background_tasks: BackgroundTasks,
                           files: List[UploadFile] = File(...)) -> JSONResponse:
    """Uploads multiple PDF-documents to the backend and assigns them to the given job ID.
    Args:
        job_id <Path_Parameter>: (uuid.UUID,  The ID of the corresponding job for the documents)
        files (List[UploadFile], optional): Uploaded files. Defaults to File(...).
    Returns:
        JSONResponse: The response as JSON.
    """
    tmp_dir = create_tmp_folder(job_id)
    if is_valid_uuid(job_id):
        file_names = []
        jobindex = [i for i in range(len(jobs)) if jobs[i].id == job_id]
        if jobindex is not None:
            job = jobs[jobindex[0]]
            job.documentdetails = []
        for file in files:
            file_name = file.filename
            if os.path.splitext(file_name)[1] != "pdf":
                raise ValueError("Please provide only PDF files.")
            file_names.append(file_name)

            # Save the file to the temporary folder
            if tmp_dir is None or not os.path.exists(tmp_dir):
                raise ValueError("Please provide a temporary folder to save the files.")

            if file_name is None:
                raise ValueError("Please provide a file to save.")
            
            with open(os.path.join(tmp_dir, file_name), "wb") as f:
                f.write(await file.read())

            if job.status == JobStatusEnum.empty:
                job.status = JobStatusEnum.working
            #Create document details
            details = Documentdetails(
                id=uuid.uuid4(),
                originalname=file_name,
                newname=os.path.splitext(file_name)[0] + '_anno' + os.path.splitext(file_name)[1],
                status=StatusEnum.new,
                errordetails=""
                created=datetime.now()
                changed=datetime.now()
            )
            job.documentdetails.append(details)
            logger.info(f"Document details {details.json()}")
        jobs[jobindex[0]] = job
        #searchresult = search_and_annotate_allpages(job, tmp_dir)
        background_tasks.add_task(search_and_annotate_allpages, job, tmp_dir)
        #To-Do: Bei Response-Code 201 muss die Antwort leer sein 
        return JSONResponse(content={"message": "Files received and saved.", "filenames": file_names})
    raise ValueError("Please provide a valid UUID for Job ID")

@app.get("/annotationjobs/{job_id}/documents/{document_id}", response_class=FileResponse, status_code=200)
async def get_document(job_id: Annotated[uuid.UUID, Path(title="The ID of the job of the documents")], 
document_id: Annotated[uuid.UUID, Path(title="The ID of the document to be retrieved")]):
    """Sends a file to caller.
    Args:
        job_id <Path_Parameter>: (uuid.UUID,  The ID of the job of the documents)
        document_id <Path_Parameter>: (uuid.UUID,  The ID of the document to be retrieved)
    Returns:
        File
    """ 
    #jobindex = next((x for x in jobs if x.id == job_id), None) #Find list element by value of class value
    if is_valid_uuid(job_id):
        jobindex = next((x for x in range(len(jobs)) if jobs[x].id == job_id), None) #Find index of list element by value of class value
        if jobindex is not None:
            currentjob = jobs[jobindex]
            if is_valid_uuid(document_id):
                documentindex = next((x for x in range(len(currentjob.documentdetails)) if currentjob.documentdetails[x].id == document_id), None) #Find list element by value of class value
                if documentindex is not None:
                    if currentjob.documentdetails[documentindex].status == StatusEnum.done_annotated:
                        return os.path.join(f"tmp_{str(job_id)}", currentjob.documentdetails[documentindex].newname)
                    raise ValueError("There were no explanations found in the document, consequently, the document wasn't saved.")
                raise ValueError("Document not found.")
            raise ValueError("Please provide a valid UUID for Document ID")
        raise ValueError("Job not found.")
    raise ValueError("Please provide a valid UUID for Job ID")
