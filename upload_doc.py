import boto3
import base64
import json
import uuid
from datetime import datetime

s3 = boto3.client('s3')
dynamo = boto3.client('dynamodb')

BUCKET = 'document-new-bucket'
TABLE = 'DocumentsTable'

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    file_data = base64.b64decode(body['file_content'])
    filename = body['filename']
    doc_id = str(uuid.uuid4())
    s3_key = f'documents/{doc_id}/{filename}'
    
    # Upload file to S3
    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=file_data)
    
    # Save metadata to DynamoDB
    dynamo.put_item(
        TableName=TABLE,
        Item={
            'DocumentId': {'S': doc_id},
            'Filename': {'S': filename},
            'S3Path': {'S': s3_key},
            'UploadDate': {'S': datetime.utcnow().isoformat()},
            'Size': {'N': str(len(file_data))}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Uploaded', 'document_id': doc_id})
    }