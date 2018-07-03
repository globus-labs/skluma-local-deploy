
import os


def file_exists(filename):
    bucket = LOADBUCKET
    key = filename
    objs = list(bucket.objects.filter(Prefix=key))
    if len(objs) > 0 and objs[0].key == key:
        print("Exists!")
    else:
        print("Doesn't exist")

def get_file(filename):

    s3 = boto3.resource('s3')
    print("Trying to download file. ")
    try:
        os.chdir("/home/skluzacek/Downloads")
    except:
        print("Already in Downloads folder. ")

    s3.Bucket('sklumabucket091817').download_file(filename, filename)
    print("Downloaded file. ")


def trash_file(filename):
    os.remove(filename)
