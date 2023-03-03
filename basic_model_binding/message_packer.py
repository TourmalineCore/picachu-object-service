import json

from model.model_result_schema import ModelResultSchema
from helpers.s3_helper import S3Helper


class MessagePacker:
    def __init__(self, model_type):
        self.model_type = model_type

    @staticmethod
    def unpack_the_message_body(message_body):
        message_str = message_body.decode('utf-8')
        message = json.loads(message_str)

        photo_id = message["photo_id"]
        photo_bytes = S3Helper() \
            .s3_download_file(file_path_in_bucket=f'/{message["path_to_photo_in_s3"]}')

        return photo_id, photo_bytes

    def pack_the_message_body(self, photo_id: int, result):
        valid_result = ModelResultSchema(
            photo_id=photo_id,
            model_type=self.model_type,
            result=result,
        )
        message_body = json.dumps(valid_result.dict()).encode('utf-8')

        return message_body
