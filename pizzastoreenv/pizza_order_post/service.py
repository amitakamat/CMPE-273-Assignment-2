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
        if event['menu_id'] and event['order_id'] and event['customer_name'] and event['customer_email']:
            event['order'] = {'selection': 'empty', 'size': 'empty', 'costs': 'empty', 'order_time': 'empty'}
            event['order_status'] = 'processing'
            response = table.put_item(Item=event)
            metadata = response.get("ResponseMetadata", None)

            if metadata is None:
                return "Create Order Failed"

            if metadata.get("HTTPStatusCode", 0) == 200:
                try:
                    pizza_store = boto3.resource('dynamodb', region_name='us-west-2').Table('PizzaStore')
                    selection = pizza_store.get_item(
                        Key={
                            'menu_id': event['menu_id']
                        }).get('Item').get('selection')

                    for i in range(0, len(selection)):
                        selection[i] = str(i + 1) + ". " + selection[i]
                        selection_list = ", ".join(selection)
                    return {
                        "Message": "Hi " + event['customer_name'] + ", please choose one of these selections:  "
                                   + selection_list
                    }
                except Exception as e:
                    return e.message
        else:
            return "Missing information. Please pass all parameters."
    except Exception as e:
        return e.message
