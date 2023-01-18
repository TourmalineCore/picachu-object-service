import argparse
from abc import ABC

from core.model_base import ModelBase
from logic import ModelLogic


class Model(ModelBase, ABC):
    def __init__(self, model_name,model_type):
        super().__init__(
            model_name=model_name,
            model_type=model_type,

        )

    def process_message(self, photo):
        print('PROCESS...')
        return ModelLogic().model_specific_logic(photo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", dest="name", type=str, help="model name", )
    parser.add_argument("-t", "--type", dest="type", type=str, help="model type", )

    args = parser.parse_args()

    model_name = args.name
    model_type = args.type

    if model_name is None:
        raise Exception("Model name is unspecified")
    if model_type is None:
        raise Exception("Model type is unspecified")

    Model(model_name=model_name,model_type=model_type).run()
