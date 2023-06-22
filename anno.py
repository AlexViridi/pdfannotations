import fitz
from annoclasses import StatusEnum, Documentdetails, Annotationjob
from loguru import logger

async def search_and_annotate_allpages(filepath, explanations: list) -> StatusEnum:
    doc = fitz.open(filepath)
    returncode = StatusEnum
    
    for page in doc:
        for explanation in explanations:
            rl = await page.search_for(explanation, quads=True)  # need a quad b/o tilted text
            # if rl is None:
            #     returncode = StatusEnum.error
            # else:
            #     returncode = StatusEnum.done
            # Status muss in Abhängigkeit gesetzt werden, ob etwas gefunden wurde
            for result in rl:
                logger.info(('coordinates ul(x,y): %d,%d ur(x,y): %d,%d ll(x,y): %d,%d rl(x,y): %d,%d' % (result.ul.x, result.ul.y, result.ur.x, result.ur.y, result.ll.x, result.ll.y, result.lr.x, result.lr.y)))
                annot = await page.add_highlight_annot(result)
            
    await doc.save(filepath, garbage=4, deflate=True, clean=True)
    doc.close
    
    return StatusEnum.done_annotated  #Temporär

async def search_and_annotate_singlepage(filepath, explanations: list, pageno) -> StatusEnum:
    doc = fitz.open(filepath)
    returncode = StatusEnum
    
    page = doc[pageno]
    for explanation in explanations:
        rl = await page.search_for(explanation, quads=True)  # need a quad b/o tilted text
        # if rl is None:
        #     returncode = StatusEnum.error
        # else:
        #     returncode = StatusEnum.done
        # Status muss in Abhängigkeit gesetzt werden, ob etwas gefunden wurde
        for result in rl:
            logger.info(('coordinates ul(x,y): %d,%d ur(x,y): %d,%d ll(x,y): %d,%d rl(x,y): %d,%d' % (result.ul.x, result.ul.y, result.ur.x, result.ur.y, result.ll.x, result.ll.y, result.lr.x, result.lr.y)))
            annot = await page.add_highlight_annot(result)
            
    await doc.save(filepath, garbage=4, deflate=True, clean=True)
    doc.close
    
    return StatusEnum.done_annotated  #Temporär 