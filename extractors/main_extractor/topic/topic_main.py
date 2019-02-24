
from .doc_vectors import docs_to_keywords, files_to_keywords, directory_to_keywords
from .pdf_to_text import extract_Text_Directly
import nltk

nltk.download('punkt')

class BadFreetextTypeException(Exception):
    """Throw this when we can't process a file. Means the input is bad. """


def extract_topic(type_arg, target_path, debug=False):

    if type_arg == 'subtext':
        # Add document as string (for partial file).
        keywords = docs_to_keywords([target_path])

    elif type_arg == 'file':

        if target_path.endswith(".pdf"):
            keywords = docs_to_keywords([extract_Text_Directly(target_path)])

        else:
            keywords = files_to_keywords([target_path])[0]

    elif type_arg == 'directory':
        # Add directory full of documents represented as files.
        keywords = directory_to_keywords([target_path])

    else:
        raise BadFreetextTypeException("Bad format for freetext topic extractor. ")

    ex_freetext = {"ex_freetext":{"type":"file", "keywords":{}, "topics":{}}}
    for item in keywords:
        if len(item[0])>20:
            ex_freetext = None
            break
        ex_freetext["ex_freetext"]["keywords"][item[0]] = str(item[1])

    if ex_freetext != None:
        ex_freetext["ex_freetext"]["topics"] = ["LDATopicNotInitialized"]

    return ex_freetext


# print(extract_topic('file', '/home/skluzacek/pub8/oceans/VOS_New_Century_2/2015/README.txt'))

# extract_topic('subtext', 'it was the best of times, it was the worst of times in Chicago, IL. ')

#Uncomment to test methods.
#print(extract_topic('file', '/home/skluzacek/Downloads/file%3A%2Fhome%2Fsuhail%2Fdataset%2FMPI_MET_data_abstract.txt'))

