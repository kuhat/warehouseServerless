import json
import boto3
from flask import request
from flask_lambda import FlaskLambda

app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
table = ddb.Table('warehouse')

@app.route('/')
def index():
    data = {
        "message": "HHHHHHHHhhhh"
    }
    return (
        json.dumps(data),
        200,
        {'Content-Type': "application/json"}
    )


@app.route('/items', methods=['GET', 'POST'])
def put_or_List_itmes():
    if request.method == 'GET':
        items = table.scan()['Items']
        return (
            json.dumps(items),
            200,
            {'Content-Type': "application/json"}
        )
    else:
        table.put_item(Item=request.form.to_dict())
        return(
            json.dumps({"message": "Items create successfully"}),
            200,
            {'Content-Type': "application/json"}
        )