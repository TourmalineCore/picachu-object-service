from core.model_result_statuses import ModelResultStatuses


class ModelResult:
    def __init__(
            self,
            photo_id: str,
            model_type,
            result: str,
            status: ModelResultStatuses = ModelResultStatuses.SUCCESSFUL,
    ):
        if not photo_id:
            raise ValueError('Photo_id should not be empty')

        if not model_type:
            raise ValueError('Model_type should not be empty')

        if not result:
            raise ValueError('Result should not be empty')

        if not status:
            raise ValueError('Status should not be empty')

        self.photo_id = photo_id
        self.model_type = model_type
        self.result = result
        self.status = status

    def __repr__(self):
        return f'<ModelResult photo_id: {self.photo_id!r} model_type:{self.model_type!r} result:{self.result!r} status:{self.status!r}>'