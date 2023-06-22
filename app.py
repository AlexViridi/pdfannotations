#app.py
import os
import uuid
from starlette.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Path
from loguru import logger
from typing import List, Optional, Annotated
from pydantic import BaseModel, ValidationError, validator

# initialize the Fast API Application.
app = FastAPI(debug=True)


class StatusEnum(IntEnum):
    new = 1
    working = 2
    done = 3
    error = 4

class Documentdetails(BaseModel):
    originalname: str
    newname: str
    id: uuid.UUID
    status: StatusEnum
    errordetails: str



class Annotationjob(BaseModel):
    id: uuid.UUID | None = None
    explanations: list

    @validator('explanations')
    def explanation_must_contain_at_least_one_Value(cls, thelist):
        if thelist is None or len(thelist) < 1:
            raise ValueError('explanations must contain at least one value ')
        return thelist



def _find_next_id():
    return max(job["id"] for job in jobs) + 1

def create_tmp_folder() -> str:
    """Creates a temporary folder for files to store.
    Returns:
        str: The directory name.
    """
    # Create a temporary folder to save the files
    tmp_dir = f"tmp_{str(uuid.uuid4())}"
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
            details = Documentdetails
            details.id = uuid.uuid4()
            details.originalname = file_name
            details.newname = os.path.splitext(file_name)[0] + '_anno' + os.path.splitext(file_name)[1]
            details.status = new
            f.write(await file.read())
    #To-Do: Enqueue documents for processing
    #embedd_documents_wrapper(folder_name=tmp_dir, aa_or_openai=aa_or_openai, token=token)
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
