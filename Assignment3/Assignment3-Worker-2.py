import json
import boto3
from collections import Counter
from random import randrange

client = boto3.client('lambda')

def lambda_handler(event, context):
    if "operation" in event:
        operation = event['operation']
    else:
        data = json.loads(event['body'])
        operation = data['operation']
    
    if operation == 'isHealthy':
        return is_healthy()
    elif operation == 'leaderProcess':
        return handle_leader_request(json.loads(event['body']))
    elif operation == 'followerProcess':
        return handle_follower_request(event)
        
    return {
        'statusCode': 400,
        'body': json.dumps('Bad Request')
    }
    
def is_healthy():
    if randrange(10) == 0:
        return {
            'statusCode': 500,
            'body': json.dumps('Worker is not available')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Worker is available')
        }
    
def handle_leader_request(event):
    available_workers = event['workers']
    book_text = event['bookText']
    
    book_size = len(book_text)
    worker_size = len(available_workers)
    spread = int(book_size / worker_size)
    
    word_list = [text.strip() for text in book_text[0:spread].split()]
    word_frequency = count_word_frequency(word_list);
    
    for worker, index in zip(available_workers, range(worker_size)):
        request_payload = {
            "operation": "followerProcess",
            "bookText": book_text[spread + index * spread:spread + (index+1) * spread],
        }
        count_response = client.invoke(
            FunctionName = worker,
            Payload = json.dumps(request_payload)
        )
        response_body = json.load(count_response['Payload'])
        word_frequency.update(json.loads(response_body['body'])['word_frequency'])
    
    return {
        'statusCode': 200,
        'body': json.dumps({"word_frequency": word_frequency})
    }
    
def handle_follower_request(event):
    book_text = event['bookText']
    
    word_list = [text.strip() for text in book_text.split()]
    word_frequency = count_word_frequency(word_list);
    
    response_body = {"word_frequency": word_frequency}
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
    
def count_word_frequency(word_list):
    return Counter(word_list)