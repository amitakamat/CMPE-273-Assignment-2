# -*- coding: utf-8 -*-
from __future__ import print_function
import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

table = dynamodb.Table('PizzaStore')


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def handler(event, context):
    try:
        sequence = '["selection", "size"]'
        event['sequence'] = json.loads(sequence)
        response = table.put_item(Item=event)
        metadata = response.get("ResponseMetadata", None)
        if metadata is None:
            return "Create Menu Failed"
        if metadata.get("HTTPStatusCode", 0) == 200:
            return "200 OK"
    except Exception as e:
        return e.message
