from kafka import KafkaConsumer, KafkaProducer

def create_consumer(topic, servers=["kafka:9092"], group_id="summerizer_group", auto_offset_reset="latest", max_poll_interval_ms=600000):
    return KafkaConsumer(
        topic,
        bootstrap_servers=servers,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        max_poll_interval_ms=max_poll_interval_ms
    )

def create_producer(servers=["kafka:9092"]):
    return KafkaProducer(bootstrap_servers=servers)

def send_message(producer, topic, message):
    producer.send(topic, message)
    producer.flush()
