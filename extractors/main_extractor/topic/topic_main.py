import os

import doc_vectors

class BadFreetextTypeException(Exception):
    """Throw this when we can't process a file. Means the input is bad. """

def extract_topic(type_arg, target_path, debug=False):

    try:
        os.chdir('topic/')
    except:
        pass

    if type_arg == 'subtext':
        # Add document as string (for partial file).
        keywords = doc_vectors.docs_to_keywords([target_path])

    elif type_arg == 'file':
        print(target_path)
        print(type_arg)
        keywords = doc_vectors.files_to_keywords([target_path])[0]

    elif type_arg == 'directory':
        # Add directory full of documents represented as files.
        keywords = doc_vectors.directory_to_keywords([target_path])

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



#Uncomment to test methods.
#print(extract_topic('file', '/home/skluzacek/Downloads/file%3A%2Fhome%2Fsuhail%2Fdataset%2FMPI_MET_data_abstract.txt'))

