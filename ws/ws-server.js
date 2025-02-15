const { Kafka } = require('kafkajs');
const WebSocket = require('ws');

const kafka = new Kafka({
  clientId: 'ws-server',
  brokers: ['kafka:9092'],
});

const consumer = kafka.consumer({ groupId: 'ws-server-group' });

const wss = new WebSocket.Server({ port: 8082 });

wss.on('connection', function connection(ws) {
  console.log('WebSocket client connected');
});

async function run() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'article_update', fromBeginning: false });
  
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      console.log(`Received Kafka message on ${topic}: ${message.value.toString()}`);
      wss.clients.forEach(function each(client) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(message.value.toString());
        }
      });
    },
  });
}

run().catch(console.error);
