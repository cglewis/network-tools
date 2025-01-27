"""
Sends message to RabbitMQ to notify capture is complete and written to a file

Created on 27 November 2019
@author: Charlie Lewis
"""
import argparse
import datetime
import json
import os

import pika
import network_tools_lib

VERSION = network_tools_lib.get_version()


def connect_rabbit(host='messenger', port=5672, queue='task_queue'):
    params = pika.ConnectionParameters(host=host, port=port)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    return channel


def send_rabbit_msg(msg, channel, exchange='', routing_key='task_queue'):
    channel.basic_publish(exchange=exchange,
                          routing_key=routing_key,
                          body=json.dumps(msg),
                          properties=pika.BasicProperties(delivery_mode=2,))
    print(' [X] %s UTC %r %r' % (str(datetime.datetime.utcnow()),
                                 str(msg['id']), str(msg['file_path'])))


def get_path(paths):
    path = None
    try:
        path = paths[0]
    except Exception as e:
        print('No path provided: {0}, quitting'.format(str(e)))
    return path


def parse_args(parser):
    parser.add_argument('paths', nargs='*')
    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == '__main__':  # pragma: no cover
    parsed_args = parse_args(argparse.ArgumentParser())
    path = get_path(parsed_args.paths)
    uid = os.environ.get('id', '')
    external_host = os.environ.get('external_host', 'messenger')
    if os.environ.get('rabbit', False) == 'true':
        try:
            channel = connect_rabbit(host=external_host)
            body = {'id': uid, 'type': 'metadata', 'file_path': path,
                    'data': '', 'file_type': 'pcap_strip',
                    'results': {'tool': 'ncapture', 'version': VERSION}}
            send_rabbit_msg(body, channel)
        except Exception as e:
            print(str(e))
