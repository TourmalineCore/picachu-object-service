from basic_model_binding.messages_traffic_controller import MessagesTrafficController
from config.model_config import model_type

if __name__ == "__main__":
    MessagesTrafficController(model_type=model_type).start_listening_to_the_queue()
