# PDF annotations
A Python backend to annotate submitted PDFs with submitted texts. The backend provides a FastAPI REST-interface. It searches transferred PDF documents for submitted texts and highlights each found text.
## usage
1. submit to-be searched texts and receive job-id
2. upload pdf-files for job-id
3. files are processed in background
4. request job status
5. download annotated files
## deployment
Pull image from docker hub (comming soon):