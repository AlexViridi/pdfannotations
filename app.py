#app.py

from flask import Flask, request, jsonify

app = Flask(__name__)

#Example data
jobs = [{"id": 0, "documents": ["file1", "file2", "file3"], "searchstrings": ["text1", "text2", "text3"]}, 
{"id": 1, "documents": ["file4", "file5", "file6"], "searchstrings": ["text4", "text5", "text6"]}, 
{"id": 2, "documents": ["file7", "file8", "file9"], "searchstrings": ["text7", "text8", "text9"]}]


def _find_next_id():
    return max(job["id"] for job in jobs) + 1

@app.get("/annotationsjobs")
def get_annotationsjobs():
    return jsonify(jobs)

@app.post("/annotationsjobs")
def create_job():
    if request.is_json:
        job = request.get_json()
        job["id"] = _find_next_id()
        jobs.append(job)
        return job, 201
    return {"error": "Request must be JSON"}, 415


@app.get("/annotationsjobs/<job_id>")
def get_annotationjob(job_id):
    return jobs[int(job_id)]

@app.get("/annotationsjobs/<job_id>/documents")
def get_documents(job_id):
    if "documents" in jobs[int(job_id)]:
        docsarray = jobs[int(job_id)]["documents"]
        return docsarray
    return {"error": "No documents array found."}

@app.get("/annotationsjobs/<job_id>/documents/<doc_id>")
def get_document(job_id, doc_id):
    return jobs[int(job_id)].documents[int(doc_id)]
