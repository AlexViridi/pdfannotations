"""API Tests."""
import os
import shutil

import httpx
import pytest
from fastapi.testclient import TestClient
from loguru import logger

from app import app, create_tmp_folder

client = TestClient(app)

def test_read_root():
    """Test the root method."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Welcome to the PDF annotation backend!"
    
def test_create_tmp_folder():
    """Test the create folder method."""
    tmp_dir = create_tmp_folder()
    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)

@pytest.mark.asyncio
async def test_job_creation():
    """Testing job creation"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/annotationjobs")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Files received and saved.",
        "filenames": ["1706.03762v5.pdf", "1912.01703v1.pdf"],
    }