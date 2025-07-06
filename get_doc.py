import boto3
import json

dynamo = boto3.client('dynamodb')
TABLE = 'DocumentsTable'

def lambda_handler(event, context):
    # Scan DynamoDB table to get all items
    response = dynamo.scan(TableName=TABLE)
    
    # Convert DynamoDB response to plain JSON (extract only needed fields)
    documents = []
    for item in response['Items']:
        documents.append({
            'DocumentId': item['DocumentId']['S'],
            'Filename': item['Filename']['S'],
            'S3Path': item['S3Path']['S'],
            'UploadDate': item['UploadDate']['S'],
            'Size': int(item['Size']['N'])
        })
    
    return {
        'statusCode': 200,
        'body': json.dumps(documents)
    }
