import json

import boto3
from flask import Flask
from flask import request
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb',
                     aws_access_key_id='AKIA4OLUM7OFO3BGXGUZ',
                     aws_secret_access_key='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')
table1 = ddb.Table('warehouse')
table2 = ddb.Table('shipper')
app = Flask(__name__)


@app.route('/items', methods=['GET', 'POST'])
def put_or_List_itmes():
    if request.method == 'GET':
        id = request.args.get('id')
        # get the item list of this shipper
        item = table2.get_item(Key={'ShipperID': str(id)}).get('Item')
        if item is None:
            msg = "No Shipper found!"
            return (msg, 400, {'Content-Type': "application/json"})
        itemList = item.get('Items')
        res = []
        for idx in itemList:
            item = table1.get_item(Key={'ShipmentID': str(idx)})['Item']
            res.append(item)
        return json.dumps(res), 200, {'Content-Type': "application/json"}
    else:
        id = request.json.get('ShipperID')
        items = request.json.get('Received')
        if id is None or items is None:
            msg = "Invalid request body!"
            return msg, 400, {'Content-Type': "application/json"}
        # Get the items that is already in the db
        oldItemsList = [item['ShipmentID'] for item in table1.scan()['Items']]
        print("oldItemList: " + str(oldItemsList))
        # Get the current shipper
        obj = table2.get_item(Key={'ShipperID': str(id)}).get('Item')
        # if the db doesn't have this shipper, add the new objs into db
        if obj is None:
            newID = max([int(item['ShipperID']) for item in table2.scan()['Items']]) + 1
            try:
                # Append shipmentID of the new items into a list
                newItemIDList = []
                with table1.batch_writer() as writer:
                    for itemObj in items:
                        # If the shipment object is already in the db, do not add it
                        if itemObj.get('ShipmentID') not in oldItemsList:
                            writer.put_item(Item=itemObj)
                        newItemIDList.append(str(itemObj.get('ShipmentID')))
                table2.put_item(Item={'ShipperID': str(newID), 'Items': newItemIDList})
                msg = "Successfully inserted new shipper and received items objects!"
                errorCode = 200
            except Exception as err:
                msg = "can not insert item into shipper and items tables: " + str(err)
                errorCode = 400
            return msg, errorCode, {'Content-Type': "application/json"}
        # If the shipper already exists in the db
        try:
            # Append shipmentID of the new items into a list
            newItemIDList = []
            with table1.batch_writer() as writer:
                for itemObject in items:
                    if itemObject.get('ShipmentID') not in oldItemsList:
                        writer.put_item(Item=itemObject)
                    newItemIDList.append(str(itemObject.get('ShipmentID')))
            # update received item list
            receivedItemList = obj.get('Items')
            for newItemid in newItemIDList:
                if newItemid not in receivedItemList:
                    receivedItemList.append(str(newItemid))
            print(str(receivedItemList))
            table2.update_item(Key={'ShipperID': str(id)},
                               UpdateExpression="set #Items = :n",
                               ExpressionAttributeNames={"#Items": "Items"},
                               ExpressionAttributeValues={":n": receivedItemList},
                               ReturnValues="UPDATED_NEW", )
            msg = "successfully updated new shipment objects and shipper db"
            errorCode = 200
        except Exception as e:
            msg = "cannot update entities: " + str(e)
            errorCode = 400
        return msg, errorCode, {'Content-Type': "application/json"}


def Get():
    items1 = table1.scan()['Items']
    print(items1)
    items2 = table2.scan()['Items']
    print(items2)
    newID = max([int(item['ShipperID']) for item in table2.scan()['Items']]) + 1
    print(newID)


def mapping():
    itemList = table2.get_item(Key={'ShipperID': "1"}).get('Item').get('Items')
    print(itemList)
    res = []
    for id in itemList:
        item = table1.get_item(Key={'ShipmentID': id})['Item']
        res.append(item)
    print(json.dumps(res))
    pass


def insert():
    objs = [
        {
            "Date": "Mar 11, 2022",
            "WarehouseID": "a908cef7-4c67-40f3-88f7-08a03ba4104e",
            "ShippingPO": "3f7b2654-052d-4a4e-905f-87f22a3877a9",
            "ShipmentID": "3",
            "BoxesRcvd": "5"
        },
        {
            "Date": "Mar 10, 2022",
            "WarehouseID": "a908cef7-4c67-40f3-88f7-08a03ba4104e",
            "ShippingPO": "71b720e3-2847-45de-bbe7-8fa099d64632",
            "ShipmentID": "4",
            "BoxesRcvd": "2"
        },
        {
            "Date": "Mar 9, 2022",
            "WarehouseID": "a908cef7-4c67-40f3-88f7-08a03ba4104e",
            "ShippingPO": "81d06bd2-39e3-427c-9fb3-4e217b9a4d60",
            "ShipmentID": "5",
            "BoxesRcvd": "12"
        }
    ]
    try:
        with table1.batch_writer() as writer:
            for obj in objs:
                writer.put_item(Item=obj)
        print("Success!!")
    except ClientError as err:
        print("Couldn't load data into table %s. Here's why: %s: %s", table1.name,
              err.response['Error']['Code'], err.response['Error']['Message'])
        raise


def update(id, receivedItemList):
    response = table2.update_item(Key={'ShipperID': str(id)},
                                  UpdateExpression="set #Items = :n",
                                  ExpressionAttributeNames={"#Items": "Items"},
                                  ExpressionAttributeValues={":n": receivedItemList},
                                  ReturnValues="UPDATED_NEW", )
    print(response["Attributes"])


def getShippers():
    items = table2.scan()['Items']
    print(items)
    res = [item.get('ShipperID') for item in items]
    print(str(res))


if __name__ == '__main__':
    # Get()
    # mapping()
    # insert()
    # app.run()
    # update('1', ['1', '2', '3'])
    getShippers()
