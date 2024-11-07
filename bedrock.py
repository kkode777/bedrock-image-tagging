# Use the native inference API to send a text message to Amazon Titan Text G1 - Express.

import boto3
import json
import base64

from botocore.exceptions import ClientError

# Create an Amazon Bedrock Runtime client.
brt = boto3.client("bedrock-runtime","us-east-1")
s3=boto3.client("s3")

bucket_name = 'kkode-s3-bucket'
image_key =  'genaiblog/images/healthy_life_style_1.pdf_page_1_figure_2.jpeg'

print(f"Getting image {image_key} from S3")
s3_response = s3.get_object(Bucket=bucket_name, Key=image_key)
image_data = s3_response['Body'].read()

# Convert image to base64
print("converting image to base64")
base64_image = base64.b64encode(image_data).decode('utf-8')
model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"

# Prepare payload for bedrock
body = json.dumps(
    {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image,
                        },
                    },
                    {"type": "text", "text": "Provide tags of the image and a one sentence summary"},
                ],
            }
        ],
    }
)

try:
    #Invoke Model
    print("Invoking model to get image description and tags")
    response = brt.invoke_model(
        modelId=model_id,
        body=body
    )

    response_body = json.loads(response.get("body").read())
    response_content=response_body['content'][0]['text']
    print(response_content)

    #add tags to DynamoDB
    print("add tags to DynamoDB")
    dynamodb = boto3.resource('dynamodb')
    table_name = 'genai_poc'  # Replace with your table name
    table = dynamodb.Table(table_name)
    
    dynamodb_response = table.put_item(
        Item={
            'objectkey': image_key,
            'tags': response_content
        }
    )

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)
