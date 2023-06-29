"""API Tests."""
import os
import shutil

import httpx
import pytest
from fastapi.testclient import TestClient
from loguru import logger
import uuid
from uuid import UUID

from app.main import create_tmp_folder, app

client = TestClient(app)

@pytest.fixture(scope="session")
def jobid():
    pytest.my_jobid = uuid.uuid4

def test_read_root():
    """Test the root method."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Welcome to the PDF annotation backend!"
    
def test_create_tmp_folder():
    """Test the create folder method."""
    tmp_dir = create_tmp_folder(str(uuid.uuid4()))
    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)

@pytest.mark.asyncio
async def test_job_creation(jobid):
    """Testing job creation"""
    jsonbody = {"explanations": ['Die Aleph Alpha Produktreihe „Luminous“ bietet verschiedene Funktionalitäten der natürlichen Sprachverarbeitung ohne nutzerspezifisches Training'], "documentdetails": []} 
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/annotationjobs", json=jsonbody)
    assert response.status_code == 200
    probejson = []
    probejson = response.json()
    assert "id" in probejson
    logger.info(f"Current value of pytest.my_jobid is {str(pytest.my_jobid)}")
    pytest.my_jobid = probejson["id"]
    logger.info(f"New value of pytest.my_jobid is {str(pytest.my_jobid)}")
    assert probejson["explanations"] == ['Die Aleph Alpha Produktreihe „Luminous“ bietet verschiedene Funktionalitäten der natürlichen Sprachverarbeitung ohne nutzerspezifisches Training']
    assert probejson["documentdetails"] == []
    assert probejson["status"] == 1
    
def test_get_jobs_still_empty(jobid):
    response = client.get("/annotationjobs")
    assert response.status_code == 200
    #Mark:
    #assert response.json() == {"id": str(pytest.my_jobid), "explanations": ['Die Aleph Alpha Produktreihe „Luminous“ bietet verschiedene Funktionalitäten der natürlichen Sprachverarbeitung ohne nutzerspezifisches Training'], "documentdetails": [], "status": 1 }

@pytest.mark.asyncio
async def test_document_upload(jobid):
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        files = [
            open("tests/ressources/test.pdf", "rb"),
        ]
        job_id = pytest.my_jobid
        response = await ac.post(
                "/annotationjobs/" + str(job_id) + "/documents", files=[("files", file) for file in files]
            )
    assert response.status_code == 200
    for entry in os.scandir():
        if entry.is_dir() and entry.name == ("tmp_" + str(job_id)):
            logger.info("temp directory created")
            assert os.path.isfile(os.path.join(entry.path, "test.pdf"))
            assert os.path.isfile(os.path.join(entry.path, "test_anno.pdf"))

@pytest.mark.asyncio
async def test_get_document(jobid):
    #/annotationjobs/{job_id}/documents
    job_id = pytest.my_jobid
    response = client.get("/annotationjobs/" + str(job_id) + "/documents")
    probejson = []
    probejson = response.json()
    documentid = probejson[0]["id"]
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        doc_response = await ac.get(
                "/annotationjobs/" + str(job_id) + "/documents/" + str(documentid)
            )
    assert doc_response.status_code == 200  
    #Mark: Wie kann ich im Response das Dokument extrahieren?
     

@pytest.mark.asyncio
async def test_job_deletion(jobid):
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        job_id = pytest.my_jobid
        response = await ac.delete(
                "/annotationjobs/" + str(job_id)
            )
    assert response.status_code == 202
    assert not os.path.isfile(os.path.join(f"tmp_{str(job_id)}", "test.pdf"))
    assert not os.path.isfile(os.path.join(f"tmp_{str(job_id)}", "test_anno.pdf"))
    