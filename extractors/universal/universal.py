
import os


import boto3

########################
def sqs_connect():
    sqs = boto3.resource('sqs', region_name='us-west-2')
    q1 = sqs.get_queue_by_name(QueueName="skluma-universal.fifo")
    return q1, sqs


def sqs_producer(file_path, file_id):
    queue = sqs_connect()
    response = queue[0].send_message(MessageBody=file_id, MessageGroupId='skluma-jobs', MessageAttributes={
                'File_To_Process': {
                'StringValue': file_path,
                'DataType': 'String'
            }
        })

    return response


# Not needed, but nice to have just in case.
def sqs_consumer(data):
    queue = sqs_connect()
    for message in queue[0].receive_messages(MessageAttributeNames=['File_To_Process']):
        # Get the custom author message attribute if it was set
        tyler_text = ''
        if message.message_attributes is not None:
            file_to_process = message.message_attributes.get('File_To_Process').get('StringValue')
            if file_to_process:
                tyler_text = ' ({0})'.format(file_to_process)

        return tyler_text


        # Print out the body and author (if set)
        # print("Receiving file with id {0} at address {1} from job queue...".format(message.body, tyler_text))
##############################3

# TODO: Step 1. Receive a file via a REST API call.
def process_file(filepath):
    size = os.stat(filepath).st_size

    # TODO: Step 2. Get the 'easy' physical metadata (i.e., name, size, extension).
    physical_metadata = {"path": filepath, "file_size": size}

    return physical_metadata


# TODO: Step 3. Get the slightly more expensive metadata (i.e., MD5 hash; checksum)
# TODO: Step 4. Write all of this information to SQLite database.
# TODO: Step 5. Notify the notebook re: which jobs have run to completion, failed, etc.


def main():
    # TODO: Pop queue. Get filename and uuid.
    # TODO: Create metadata element for it in DB.

    # while True:
    filename = sqs_consumer("nothing")
    universal_metadata = process_file(filename)
    print(universal_metadata)
