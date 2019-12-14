"""

"""
import confluent_kafka


def start_consumer(bootstrap_server, group_id, topics):
    """
    Start Kafka consumer
    :param bootstrap_server: address of the bootstrap server, e.g. localhost:9092
    :param group_id: group id for consumer
    :param topics: list of topics to subscribe to
    :return:
    """
    consumer = confluent_kafka.Consumer({"bootstrap.servers":bootstrap_server, "group.id":group_id})
    consumer.subscribe(topics)
    return consumer


def get_stream(consumer):
    """
    Return infinite generator for messages polled from consumer
    :param consumer:
    :return:
    """
    while True:
        msg = consumer.poll(1)
        if msg is None:
            continue
        if 'No more messages' in str(msg.value()):
            continue
        yield str(msg.value(), 'utf-8')


def get_msg(consumer, timeout=1):
    """
    Return message polled from Kafka consumer
    :param consumer:
    :param timeout: any value <= 0 will use blocking message poll
    :return:
    """
    msg = None
    if timeout > 0:
        msg = consumer.poll(timeout)
    else:
        msg = consumer.poll()

    if msg and not msg.error():
        msg = msg.value()
    else:
        msg = None
    return msg


def get_msg_topic(consumer, timeout=1):
    """
    Return message and its topic from Kafka consumer
    :param consumer:
    :param timeout: any value <= 0 will use blocking message poll
    :return:
    """
    msg = None
    if timeout > 0:
        msg = consumer.poll(timeout)
    else:
        msg = consumer.poll()

    if msg and not msg.error():
        msg = {'value': msg.value(), 'topic': msg.topic()}
    else:
        msg = None
    return msg


if __name__ == "__main__":
    import argparse
    import time
    parser = argparse.ArgumentParser(description='Start Kafka Consumer')
    parser.add_argument('--server', '-s', default='localhost:9092')
    parser.add_argument('--groupid','-g', default='warrior')
    parser.add_argument('--topics', '-t', nargs='+', default=['mytopic'])
    args = parser.parse_args()
    print("STARTING", args)
    consumer = start_consumer(args.server, args.groupid, args.topics)
    prev = None
    msg = None
    while True:
        prev = msg
        msg = get_msg(consumer)
        if msg:
            if prev is None:
                print()
            print(msg, flush=True)
        else:
            print('.', end='', flush=True)
    time.sleep(3)

