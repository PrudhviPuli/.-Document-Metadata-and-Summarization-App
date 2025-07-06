import boto3
import json
from decimal import Decimal
import datetime

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    print("Event received:", event)
    s3 = boto3.client('s3')
    bedrock = boto3.client('bedrock-runtime')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Documents')
    
    try:
        # Extract DocumentId and UploadDate from pathParameters or queryStringParameters
        path_params = event.get('pathParameters', {})
        query_params = event.get('queryStringParameters', {})
        doc_id = path_params.get('documentId') or query_params.get('documentId')
        upload_date = path_params.get('uploadDate') or query_params.get('uploadDate')
        print("Document ID:", doc_id)
        print("Upload Date:", upload_date)
        
        if not doc_id or not upload_date:
            raise Exception("Both DocumentId and UploadDate are required.")
        
        # Get metadata using composite key
        item_response = table.get_item(Key={'DocumentId': doc_id, 'UploadDate': upload_date})
        if 'Item' not in item_response:
            raise Exception(f"DocumentId {doc_id} with UploadDate {upload_date} not found in DynamoDB")
        item = item_response['Item']
        print("DynamoDB item:", item)
        
        # Fetch from S3 (use S3Path)
        response = s3.get_object(Bucket='my-docs-bucket-a', Key=item['S3Path'])
        print("S3 object fetched")
        content = response['Body'].read().decode('utf-8')
        
        # Generate summary
        prompt = f"""\n\nHuman: Summarize this in 3 bullet points:\n{content[:10000]}\n\nAssistant:"""
        print("Prompt ready, calling Bedrock")
        bedrock_response = bedrock.invoke_model(
            modelId='anthropic.claude-instant-v1',
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 300
            })
        )
        print("Bedrock response received")
        summary = json.loads(bedrock_response['body'].read())['completion']
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary': summary,
                'metadata': item
            }, cls=DecimalEncoder)  # Use custom encoder here
        }
    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}, cls=DecimalEncoder)
        }