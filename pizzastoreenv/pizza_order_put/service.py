# -*- coding: utf-8 -*-
from __future__ import print_function
import boto3
import json
import decimal
import time

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
        input_value = event['input']
        if input_value:

            try:
                pizza_menu = boto3.resource('dynamodb', region_name='us-west-2').Table('PizzaStore')
            except Exception as e:
                return e.message

            item = table.get_item(
                Key={
                    'order_id': event['order_id']
                }).get('Item')
            if item is None:
                return {
                    "Message": "Please enter a valid order number."
                }
            order = item.get('order')
            menu_id = item.get('menu_id')
            if order.get('selection') == 'empty':

                menu = pizza_menu.get_item(
                    Key={
                        'menu_id': menu_id
                    }).get('Item')

                selection = menu.get('selection')[int(input_value) - 1]
                order['selection'] = selection

                sizes = menu.get('size')
                for i in range(0, len(sizes)):
                    sizes[i] = str(i + 1) + ". " + sizes[i]
                    sizes_list = ", ".join(sizes)
                    response = {
                        "Message": "Which size do you want? " + sizes_list
                    }

            else:
                if order.get('size') == 'empty':
                    menu = pizza_menu.get_item(
                        Key={
                            'menu_id': menu_id
                        }).get('Item')
                    size = menu.get('size')[int(input_value) - 1]
                    order['size'] = size
                    cost = menu.get('price')[int(input_value) - 1]
                    order['costs'] = cost
                    response = {
                        "Message": "Your order costs $" + cost + ". We will email you when the order is ready. Thank you!"
                    }
                    order['order_time'] = time.strftime("%m-%d-%Y@%H:%M:%S")
                else:
                    response = {
                        "Message": "Your order is being processed. You will receive an email when the order is ready. Thank you!"
                    }


            update_response = table.update_item(
                Key={
                    'order_id': event['order_id']
                },
                UpdateExpression="SET #order = :ss",
                ExpressionAttributeNames={
                    '#order': 'order'
                },
                ExpressionAttributeValues={
                    ':ss': order
                }
            )
            metadata = update_response.get("ResponseMetadata", None)
            if metadata is None:
                return "Order Update Failed"
            if metadata.get("HTTPStatusCode", 0) == 200:
                return response
    except Exception as e:
        return e.message
