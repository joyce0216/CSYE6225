import json
import boto3
import random
import urllib.request, urllib.error, urllib.parse

client = boto3.client('lambda')

worker_set = {
    'Assignment3-Worker-1',
    'Assignment3-Worker-2',
    'Assignment3-Worker-3'
}

def lambda_handler(event, context):
    available_workers = get_available_workers()
    
    if len(available_workers) > 0:
        leader = elect_leader(available_workers)
        return {
            'statusCode': 200,
            'body': json.dumps({"availableWorkers": available_workers, "leader": leader})
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps("No workers available")
        }
    

def get_available_workers():
    available_workers = []
    
    for worker in worker_set:
        # Check worker's availablity
        response = client.invoke(
            FunctionName = worker,
            Payload = '{"operation": "isHealthy"}'
        )
        
        response_payload = json.load(response['Payload'])
        
        # Add healthy worker to worker list
        if response_payload['statusCode'] is 200: 
            available_workers.append(worker)
        
    return available_workers
    
def elect_leader(available_workers):
    return random.choice(available_workers)
    
