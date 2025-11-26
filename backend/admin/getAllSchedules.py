import json
import boto3
from operator import itemgetter

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CLASSES')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    }

    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    try:
        # Scan table to get all items
        response = table.scan()
        all_items = response['Items']
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            all_items.extend(response['Items'])
        
        # Sort by user_id (ewan ko ba kung by user_id, class_id, o creation date dapat)
        # all_items.sort(key=lambda x: x.get('user_id', ''), reverse=False) 
        
        keys_to_exclude = ["user_id"]
        # creates unique classes, in spite of repeat users in the same class
        # the key in the dictionary comprehension will create uniqueness
        unique_items = list(
            {
                (item['class_code'], item['days_of_week'], 
                item['location'], item['professor'], 
                item['time_end'], item['time_start']):
                {k:v for k, v in item.items() if k not in keys_to_exclude} 
                for item in all_items
            }.values()
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(unique_items)
        }

    # TODO implement
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Failed to retrieve characters',
                'details': str(e)
            })
        }
    
