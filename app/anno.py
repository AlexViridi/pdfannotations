import fitz
from app.annoclasses import StatusEnum, Documentdetails, Annotationjob, JobStatusEnum
from loguru import logger
import os
from datetime import datetime

def search_and_annotate_allpages(annotationjob: Annotationjob, tmp_path: str):
    """Annotates all PDFs of an annotation-job with all found explanations.
    Args:
        annotationjob: Annotationjob 
    Returns:
        ./. (async)
    """  
    for document in annotationjob.documentdetails:
        doc = fitz.open(os.path.join(tmp_path, document.originalname))
        document.status = StatusEnum.working
        document.changed = datetime.now()
        pagenumber = 1
        requires_save = False
        for page in doc:
            for explanation in annotationjob.explanations:
                rl = page.search_for(explanation, quads=True)  # need a quad b/o tilted text
                for result in rl:
                    logger.debug('Explanation %s found in %s on page %i' % (explanation, document.originalname, pagenumber))
                    annot = page.add_highlight_annot(result)
                    document.changed = datetime.now()
                    requires_save = True
            pagenumber += 1    
        if requires_save:
            doc.save(os.path.join(tmp_path, document.newname), garbage=4, deflate=True, clean=True)
            logger.debug('Document %s saved as %s' % (document.originalname, document.newname))
            document.status = StatusEnum.done_annotated
            document.changed = datetime.now()
            document.finished = datetime.now()
            timediff = document.finished - document.created
            seconds_in_day = 24 * 60 * 60
            logger.debug('Document %s took %d mins and %d seconds and %d milliseconds to process.' % (document.originalname, 
                                                                      divmod(timediff.days * seconds_in_day + timediff.seconds, 60)[0],
                                                                      divmod(timediff.days * seconds_in_day + timediff.seconds, 60)[1], timediff.microseconds // 1000))
        else:
            document.status = StatusEnum.done_not_annotated
            logger.info('Document %s not saved, because no explanations found.' % (document.originalname))
            document.changed = datetime.now()
            document.finished = datetime.now()
        doc.close
    annotationjob.status = JobStatusEnum.done
    logger.debug('Job %s done.' % (str(annotationjob.id)))