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
        response = table.get_item(
            Key={
                'menu_id': event['menu_id']
            })
        if response['Item'] is None:
            return "Failed to retrieve menu."
        else:
            item = response['Item']
            #return json.dumps(item)
            return item
    except Exception as e:
        return e.message
