import fitz
from annoclasses import StatusEnum, Documentdetails, Annotationjob
from loguru import logger
import os

def search_and_annotate_allpages(annotationjob: Annotationjob, tmp_path: str):
    for document in annotationjob.documentdetails:
        doc = fitz.open(os.path.join(tmp_path, document.originalname))
        document.status = StatusEnum.working
        pagenumber = 1
        requires_save = False
        for page in doc:
            for explanation in annotationjob.explanations:
                rl = page.search_for(explanation, quads=True)  # need a quad b/o tilted text
                for result in rl:
                    logger.info('Explanation %s found in %s on page %i' % (explanation, document.originalname, pagenumber))
                    annot = page.add_highlight_annot(result)
                    requires_save = True
            pagenumber += 1    
        if requires_save:
            doc.save(os.path.join(tmp_path, document.newname), garbage=4, deflate=True, clean=True)
            logger.info('Document %s saved as %s' % (document.originalname, document.newname))
            document.status = StatusEnum.done_annotated
        else:
            document.status = StatusEnum.done_not_annotated
        doc.close
        return True