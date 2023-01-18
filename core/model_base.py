import json
import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime

from pika import ConnectionParameters, PlainCredentials, BlockingConnection
from pika.exceptions import ConnectionClosedByBroker, AMQPChannelError, AMQPConnectionError

from core.model_result import ModelResult
from core.model_result_producer import ModelResultProducer
from core.model_result_statuses import ModelResultStatuses
from helpers.s3_helper import S3Helper
from infrastructure.rabbitmq.rabbitmq_config_provider import RabbitMQConfigProvider

(
    rabbitmq_host,
    rabbitmq_username,
    rabbitmq_password,
) = RabbitMQConfigProvider.get_broker_config()

(
    rabbitmq_blocked_connection_timeout,
    rabbitmq_heartbeat,
    rabbitmq_models_max_retry_number,
    rabbitmq_models_retry_delay_ms,
) = RabbitMQConfigProvider.get_consumption_config()

exchanges_config = RabbitMQConfigProvider.get_exchange_names_config()

requests_exchange_name = exchanges_config.rabbitmq_requests_exchange_name
models_queues_dlx = exchanges_config.rabbitmq_models_queues_dlx_name
models_retry_queue_dlx = exchanges_config.rabbitmq_models_retry_queue_dlx_name

queues_config = RabbitMQConfigProvider.get_queue_names_config()

models_retry_queue_name = queues_config.rabbitmq_models_retry_queue_name


class ModelBase(ABC):
    def __init__(self, model_name,model_type):
        super().__init__()

        self.model_name = model_name
        self.model_type = model_type

        self.result_producer = ModelResultProducer(
            self.model_name,
        )

    def get_queue_name(self):
        return f'{self.model_name}-queue'

    def run(self):
        model_queue_name = self.get_queue_name()
        print('Model with queue={0} started'.format(model_queue_name))

        parameters = ConnectionParameters(
            host=str(rabbitmq_host),
            virtual_host='/',
            credentials=PlainCredentials(rabbitmq_username, rabbitmq_password),
            blocked_connection_timeout=rabbitmq_blocked_connection_timeout,
            heartbeat=rabbitmq_heartbeat,
        )

        while True:
            try:
                logging.warning(f'Connecting to RabbitMQ: {rabbitmq_host}')
                connection = BlockingConnection(parameters)

                channel = connection.channel()
                channel.exchange_declare(exchange=requests_exchange_name, exchange_type='fanout')
                # dead message exchange where goes rejected messages
                channel.exchange_declare(exchange=models_queues_dlx, exchange_type='direct')
                # dead message exchange where goes expired messaged from delayed retry queue
                channel.exchange_declare(exchange=models_retry_queue_dlx, exchange_type='direct')
                channel.basic_qos(prefetch_count=1)  # Process and acknowledge only one message at a time

                channel.queue_declare(
                    queue=model_queue_name,
                    arguments={
                        "x-dead-letter-exchange": models_queues_dlx,
                        'x-dead-letter-routing-key': model_queue_name
                    },
                    durable=True,  # need to persist the queue that should survive the broker restart
                    exclusive=False,  # any consumer can connect to the queue, not only this one
                    auto_delete=False,  # don't delete the queue when consumer disconnects
                )

                channel.queue_declare(
                    queue=models_retry_queue_name,
                    arguments={
                        'x-message-ttl': rabbitmq_models_retry_delay_ms,
                        "x-dead-letter-exchange": models_retry_queue_dlx,
                    },
                    durable=True,  # need to persist the queue that should survive the broker restart
                    exclusive=False,  # any consumer can connect to the queue, not only this one
                    auto_delete=False,  # don't delete the queue when consumer disconnects
                )

                channel.queue_bind(exchange=requests_exchange_name, queue=model_queue_name)
                # transfer rejected messages from searchers queues to delayed retry queue specifying searcher queue name as routing key
                channel.queue_bind(exchange=models_queues_dlx, queue=models_retry_queue_name,
                                   routing_key=model_queue_name)
                # transfer expired messages from delayed retry queue from only this searcher to its queue by the routing key
                channel.queue_bind(exchange=models_retry_queue_dlx, queue=model_queue_name,
                                   routing_key=model_queue_name)

                channel.basic_consume(model_queue_name, self.on_message)
                channel.start_consuming()

            except (ConnectionClosedByBroker, AMQPConnectionError):
                logging.info('Connection was closed, retrying...')
                # continue

            except AMQPChannelError:
                logging.error('Caught a channel error: {0}, stopping...'.format(repr(traceback.format_exc())))
                # break

            except Exception:
                logging.error('Unexpected error occurred: {0}'.format(repr(traceback.format_exc())))

    def on_message(self, channel, method_frame, header_frame, body):
        message_str = body.decode('utf-8')
        logging.debug(f'Message Received {message_str}')
        message = json.loads(message_str)

        photo_bytes = S3Helper().s3_download_file(file_path_in_bucket=f'/{message["path_to_photo_in_s3"]}')
        retry_count = find_retry_count(header_frame)

        request_processing_started_at_utc = datetime.utcnow()
        try:
            logging.debug('Message processing started at={0}'.format(request_processing_started_at_utc))

            model_result = self.process_message(photo_bytes)

            result = ModelResult(
                photo_id=message['photo_id'],
                model_type=self.model_type,
                result=model_result,
                status=ModelResultStatuses.SUCCESSFUL,
            )

            self.result_producer.produce_successful_message(
                result
            )

            logging.debug('Message processing finished at={0}'.format(datetime.utcnow()))

        except Exception as e:
            logging.error('Unexpected error occurred: {0}'.format(repr(traceback.format_exc())))

            if retry_count >= rabbitmq_models_max_retry_number:
                result_type = f'{self.model_name}-result'

                self.result_producer.produce_failed_message(
                    message,
                    result_type,
                )
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                logging.info('Cannot be processed (acknowledged)')
            else:
                channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=False)
                logging.info('Message rejected')
            return

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        logging.info('Done (acknowledged)')

    @abstractmethod
    def process_message(self, message):
        pass


def find_retry_count(header_frame):
    retry_count = 0
    if header_frame.headers is not None and 'x-death' in header_frame.headers:
        retry_count = header_frame.headers['x-death'][0]['count']
    return retry_count
