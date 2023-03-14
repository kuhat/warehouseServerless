import json
import boto3
from flask import request
from flask_lambda import FlaskLambda

app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb',
                     aws_access_key_id='AKIA4OLUM7OFO3BGXGUZ',
                     aws_secret_access_key='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')
table1 = ddb.Table('warehouse')
table2 = ddb.Table('shipper')


@app.route('/')
def index():
    data = {
        "message": "This api works!"
    }
    return (
        json.dumps(data),
        200,
        {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}
    )


# Get all the shippers
@app.route('/shippers', methods=['GET'])
def getShippers():
    try:
        items = table2.scan()['Items']
        res = [item.get('ShipperID') for item in items]
        data = {
            "data": res
        }
        return json.dumps(data), 200, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}
    except Exception as e:
        data = {
            "data": str(e)
        }
        return json.dumps(data), 400, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}


@app.route('/items', methods=['GET', 'POST'])
def put_or_List_itmes():
    if request.method == 'GET':
        id = request.args.get('id')
        # get the item list of this shipper
        item = table2.get_item(Key={'ShipperID': str(id)}).get('Item')
        if item is None:
            msg = "No Shipper found!"
            return (msg, 400, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"})
        itemList = item.get('Items')
        res = []
        for idx in itemList:
            item = table1.get_item(Key={'ShipmentID': str(idx)})['Item']
            res.append(item)
        return json.dumps(res), 200, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}
    else:
        id = request.json.get('ShipperID')
        items = request.json.get('Received')
        if id is None or items is None:
            msg = "Invalid request body!"
            return msg, 400, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}
        # Get the items that is already in the db
        oldItemsList = [item['ShipmentID'] for item in table1.scan()['Items']]

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
            return msg, errorCode, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}
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
            table2.update_item(Key={'ShipperID': str(id)},
                               UpdateExpression="set #Items = :n",
                               ExpressionAttributeNames={"#Items": "Items"},
                               ExpressionAttributeValues={":n": receivedItemList},
                               ReturnValues="UPDATED_NEW", )
            msg = "successfully updated new shipment objects and shipper db"
            errorCode = 200
        except Exception as e:
            msg = "cannot update entities"
            errorCode = 400
        return msg, errorCode, {'Content-Type': "application/json", "Access-Control-Allow-Origin": "*"}
