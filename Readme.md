# PDF annotations
A Python backend to annotate submitted PDFs with submitted texts. The backend provides a FastAPI REST-interface. It searches transferred PDF documents for submitted texts and highlights each found text.

- [PDF annotations](#pdf-annotations)
  - [Usage](#usage)
    - [Create job](#create-job)
    - [Upload PDF files](#upload-pdf-files-for-job-id)
    - [Request job/document status](#request-jobdocument-status)
    - [Download annotated file](#download-annotated-files)
    - [Delete job and documents](#delete-job-and-documents)
  - [Deployment](#deployment)
## usage
### Create job
submit to-be searched texts (i.e. explanations) and receive job-id
```bash
curl -X 'POST' \
  'http://127.0.0.1:80/annotationjobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "explanations": [
    "imperdiet enim"
  ]
  }'
```
You need to extract the job-id from response, e.g. `$.id`:
```json
{
  "id": "0d8e9361-4c75-4879-8269-482ccf8c1994",
  "explanations": [
    "imperdiet enim"
  ],
  "documentdetails": null,
  "status": 1
}
```
### upload pdf-files for job-id
```bash
curl -X 'POST' \
  'http://127.0.0.1:80/annotationjobs/0d8e9361-4c75-4879-8269-482ccf8c1994/documents' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@test.pdf;type=application/pdf'
```
### files are processed in background
### request job/document status
you can either query the job's status including all its documents...:
```bash
curl -X 'GET' \
  'http://127.0.0.1:80/annotationjobs/0d8e9361-4c75-4879-8269-482ccf8c1994/documents' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "originalname": "test.pdf",
    "newname": "test_anno.pdf",
    "id": "fc6d6261-7e57-4471-b465-1cb769a399e3",
    "status": 4,
    "errordetails": "",
    "created": "2023-07-28T16:38:59.203704",
    "changed": "2023-07-28T16:38:59.274759",
    "finished": "2023-07-28T16:38:59.274767"
  }
]
```
...or the status of all jobs:
```bash
curl -X 'GET' \
  'http://127.0.0.1:80/annotationjobs' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "id": "0d8e9361-4c75-4879-8269-482ccf8c1994",
    "explanations": [
      "imperdiet enim"
    ],
    "documentdetails": [
      {
        "originalname": "test.pdf",
        "newname": "test_anno.pdf",
        "id": "fc6d6261-7e57-4471-b465-1cb769a399e3",
        "status": 4,
        "errordetails": "",
        "created": "2023-07-28T16:38:59.203704",
        "changed": "2023-07-28T16:38:59.274759",
        "finished": "2023-07-28T16:38:59.274767"
      }
    ],
    "status": 3
  }
]
```
Job status `"status": 3` (`done = 3`) means the job is done, 2 indicates work in progress.
Document `"status": 4` (`done_annotated = 4`) indicates that the text was found and the document has been successfully annotated. Document-status 3 means that the text wasn't found and therefore, no annotations have been added.
### download annotated files
If document status equals 4, the annotated document can be downloaded (filename: original file name + suffix "_anno"):
```bash
curl -X 'GET' \
  'http://127.0.0.1:80/annotationjobs/0d8e9361-4c75-4879-8269-482ccf8c1994/documents/fc6d6261-7e57-4471-b465-1cb769a399e3' \
  -H 'accept: */*'
```
Response:
*File download*
### Delete job and documents
After downloading the annotated documents the job and its documents shall be deleted:
```bash
curl -X 'DELETE' \
  'http://127.0.0.1:80/annotationjobs/0d8e9361-4c75-4879-8269-482ccf8c1994' \
  -H 'accept: application/json'
```
## deployment
Clone repository, then
```bash
cd pdfannotations
```
You can use docker compose...:
```bash
docker compose up
```
...or alternatively, you can build the container on your own:
```bash
docker build - < Dockerfile
```
The service is now running on your localhost and can be reached via http://127.0.0.1