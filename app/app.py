import os
import boto3
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, Response, render_template, redirect

app = Flask(__name__)

# connecting to dynamodb aws instance
client = boto3.client('dynamodb', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamoTableName = 'PostsTable'
table = dynamodb.Table(dynamoTableName)


@app.route("/healthcheck")
def hello():
    return Response('ok', 200)


@app.route("/api/v1/posts")
def get_posts():

    table = dynamodb.Table(dynamoTableName)
    items = table.scan()['Items']

    if len(items) == 0:
        return jsonify({'error': 'There is nothing to show'}), 404

    return jsonify(items)


@app.route("/api/v1/post", methods=["POST"])
def create_post():
    author = request.json.get('author')
    content = request.json.get('content')
    date = datetime.now().isoformat()
    post_id = str(uuid.uuid4())

    if not author or not content:
        return jsonify({'error': 'Please specify post author and its content'}), 400

    # write item into dynamodb
    resp = client.put_item(
        TableName=dynamoTableName,
        Item={
            # get unique id
            'id': {'S': post_id},
            'author': {'S': author},
            'content': {'S': content},
            'date': {'S': date}
        }
    )

    # return posted item
    return jsonify({
        'id': post_id,
        'author': author,
        'content': content,
        'date': date
    })


@app.route("/")
def redirect_to_posts():
    return redirect("/posts")


@app.route("/post", methods=["POST"])
def create_post_from_form():
    author = request.form.get('author')
    content = request.form.get('content')
    date = datetime.now().isoformat()
    post_id = str(uuid.uuid4())

    resp = client.put_item(
        TableName=dynamoTableName,
        Item={
            # get unique id
            'id': {'S': post_id},
            'author': {'S': author},
            'content': {'S': content},
            'date': {'S': date}
        }
    )

    # redirect to the main page after creating new post
    return redirect("/posts", code=302)


@app.route("/posts")
def render_posts():
    items = table.scan()['Items']
    items = sorted(items, key=lambda x: x['date'], reverse=True)
    for item in items:
        item['date'] = datetime.fromisoformat(item['date']).strftime("%d.%m.%Y %H:%M")
    return render_template('template.html', items=items)


if __name__ == '__main__':
    app.run(threaded=True,host='0.0.0.0',port=5000)

