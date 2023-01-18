import json
import uuid
import logging
from datetime import datetime

import pika

from core.model_result import ModelResult
from infrastructure.rabbitmq.rabbitmq_config_provider import RabbitMQConfigProvider

(
    rabbitmq_host,
    rabbitmq_username,
    rabbitmq_password,
) = RabbitMQConfigProvider.get_broker_config()

queue_name = RabbitMQConfigProvider.get_queue_names_config().rabbitmq_results_queue_name


class ModelResultProducer:
    def __init__(
            self,
            model_type,
    ):
        super().__init__()
        self.model_type = model_type

    def produce_successful_message(
            self,
            result,
    ):
        if not isinstance(result, ModelResult):
            raise ValueError('result should be an instance of ModelResult')

        self._produce_result_message(
            result
        )

    # def produce_failed_message(
    #         self,
    #         request_message,
    #         client_request_id,
    #         result_type,
    #         request_processing_started_at_utc,
    # ):
    #     failed_result = ModelResult(
    #         'Result generation failed.',
    #         {},  # empty object because it's not nullable column in sf-api db
    #         result_type,
    #         1,
    #         ModelResultStatuses.failed,
    #     )
    #
    #     self._produce_result_message(
    #         client_request_id,
    #         failed_result,
    #         request_processing_started_at_utc,
    #     )

    def _produce_result_message(
            self,
            result: ModelResult,
    ):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_host,
                virtual_host='/',
                credentials=pika.credentials.PlainCredentials(rabbitmq_username, rabbitmq_password)
            )
        )
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        # body = {
        #     'version': 3,
        #     'searchingParameters': request_message,
        #     'result': {
        #         'description': searcher_result.description,
        #         'data': searcher_result.data,
        #         'resultType': searcher_result.result_type,
        #         'status': searcher_result.status.value,
        #         'schemaVersion': searcher_result.schema_version
        #     },
        #     'meta': {
        #         'searcher': {
        #             'searcherType': self.searcher_type,
        #             'searcherSessionId': self.searcher_session_id,
        #             'processingOccurrenceNumber': self.requests_stream_processing_occurrence_number,
        #             'messageId': str(uuid.uuid4()),
        #             'messageSentAtUtc': str(datetime.utcnow()),
        #             'requestProcessingStartedAtUtc': str(request_processing_started_at_utc)
        #         }
        #     }
        # }

        body_str = json.dumps(result.__dict__)
        print(body_str)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=body_str.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

        # ToDo should we log entire body?
        logging.info(f'Searching result sent to: {queue_name} - {body_str}')
