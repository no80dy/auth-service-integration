import json

from pydantic_classes import Genre, Person


class Transformer():
    """Класс для валидации данных из Postgres и приведения к формату для загрузки в Elasticsearch."""

    def __init__(self, schema: str):
        if schema in ('genres', 'persons'):
            self.schema = schema
        else:
            raise ValueError(
                f'{self.__class__.__name__}: Unknown schema name: {schema}')

    def _transform_record(self, record) -> str:
        """Метод для преобразования записи из базы данных в объект JSON по схеме Elasticsearch."""
        if self.schema == 'genres':
            transformed_record = Genre(**record)
            return transformed_record.model_dump_json()
        elif self.schema == 'persons':
            transformed_record = Person(**record)
            return transformed_record.model_dump_json()

    def _transform_row_before_record(self, record_id: str) -> str:
        """Метод формирования строки необходимой для формирования пачки записей по формату Elasticsearch"""
        row_before_record = {"index": {
            "_index": f"{self.schema}",
            "_id": None
        }}
        row_before_record['index']['_id'] = record_id
        return json.dumps(row_before_record)

    def transform_batch_records(self, batch_records: list) -> str:
        """Преобразует пачку записей из базы данных в пачку для загрузки по формату ES."""
        transformed_batch_records = ''

        for record in batch_records:
            transformed_row_before_record = self._transform_row_before_record(
                record['id'])
            transformed_record = self._transform_record(record)

            transformed_batch_records += transformed_row_before_record + \
                '\n' + transformed_record + '\n'
        return transformed_batch_records
