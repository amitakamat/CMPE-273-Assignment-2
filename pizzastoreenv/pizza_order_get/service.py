# -*- coding: utf-8 -*-
from __future__ import print_function
import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

table = dynamodb.Table('Orders')


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
        order_value = event['order_id']
        if order_value:
            try:
                item = table.get_item(
                    Key={
                        'order_id': order_value
                    }).get('Item')
                if item:
                    return item
                else:
                    return {
                        "Message": "The order id is not valid."
                    }
            except Exception as e:
                return e.message
        else:
            return {
                "Message": "ID missing. Please pass order id."
            }
    except Exception as e:
        return e.message
