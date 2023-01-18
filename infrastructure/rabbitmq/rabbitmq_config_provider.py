import os


def get_required_env_variable(name: str):
    env_variable_value = os.getenv(name)
    if env_variable_value is None:
        raise ValueError(f'You should specify required env variable: {name}.')
    return env_variable_value


def get_required_env_variable_as_int(name: str):
    env_variable_value = os.getenv(name)
    if env_variable_value is None:
        raise ValueError(f'You should specify required env variable: {name}.')
    return int(get_required_env_variable(name))


rabbitmq_host = get_required_env_variable('RABBITMQ_HOST')
rabbitmq_username = get_required_env_variable('RABBITMQ_DEFAULT_USER')
rabbitmq_password = get_required_env_variable('RABBITMQ_DEFAULT_PASS')

rabbitmq_blocked_connection_timeout = get_required_env_variable_as_int('RABBITMQ_BLOCKED_CONNECTION_TIMEOUT')
rabbitmq_heartbeat = get_required_env_variable_as_int('RABBITMQ_HEARTBEAT')
rabbitmq_models_max_retry_number = get_required_env_variable_as_int('RABBITMQ_MODELS_MAX_RETRY_NUMBER')
rabbitmq_models_retry_delay_ms = get_required_env_variable_as_int('RABBITMQ_MODELS_RETRY_DELAY_MS')
rabbitmq_requests_exchange_name = get_required_env_variable('RABBITMQ_REQUESTS_EXCHANGE_NAME')
rabbitmq_models_queues_dlx_name = get_required_env_variable('RABBITMQ_MODELS_QUEUES_DLX_NAME')
rabbitmq_models_retry_queue_name = get_required_env_variable('RABBITMQ_MODELS_RETRY_QUEUE_NAME')
rabbitmq_models_retry_queue_dlx_name = get_required_env_variable('RABBITMQ_MODELS_RETRY_QUEUE_DLX_NAME')
rabbitmq_results_queue_name = get_required_env_variable('RABBITMQ_RESULTS_QUEUE_NAME')


class ExchangeNamesConfig:
    def __init__(self):
        super().__init__()
        self.rabbitmq_requests_exchange_name = rabbitmq_requests_exchange_name
        self.rabbitmq_models_queues_dlx_name = rabbitmq_models_queues_dlx_name
        self.rabbitmq_models_retry_queue_dlx_name = rabbitmq_models_retry_queue_dlx_name


class QueueNamesConfig:
    def __init__(self):
        super().__init__()
        self.rabbitmq_results_queue_name = rabbitmq_results_queue_name
        self.rabbitmq_models_retry_queue_name = rabbitmq_models_retry_queue_name


class RabbitMQConfigProvider:
    @staticmethod
    def get_broker_config():
        return (
            rabbitmq_host,
            rabbitmq_username,
            rabbitmq_password,
        )

    @staticmethod
    def get_consumption_config():
        return (
            rabbitmq_blocked_connection_timeout,
            rabbitmq_heartbeat,
            rabbitmq_models_max_retry_number,
            rabbitmq_models_retry_delay_ms,
        )

    @staticmethod
    def get_queue_names_config():
        return QueueNamesConfig()

    @staticmethod
    def get_exchange_names_config():
        return ExchangeNamesConfig()
