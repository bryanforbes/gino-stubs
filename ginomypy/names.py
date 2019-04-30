from typing_extensions import Final

COLUMN_NAME: Final = 'sqlalchemy.sql.schema.Column'
GINO_NAME: Final = 'gino.api.Gino'
DECLARATIVE_BASE_NAME: Final = 'gino.declarative.declarative_base'
CRUD_CLASS_CREATE_NAME: Final = 'gino.crud._CreateWithoutInstance.__call__'
CRUD_UPDATE_NAME: Final = 'gino.crud._UpdateWithInstance.__call__'
CRUD_UPDATE_REQUEST_NAME: Final = 'gino.crud.UpdateRequest.update'
VALUES_NAMES: Final = {
    CRUD_CLASS_CREATE_NAME,
    CRUD_UPDATE_NAME,
    CRUD_UPDATE_REQUEST_NAME,
}
JSON_STRING: Final = 'gino.json_support.StringProperty'
JSON_DATETIME: Final = 'gino.json_support.DateTimeProperty'
JSON_INTEGER: Final = 'gino.json_support.IntegerProperty'
JSON_BOOLEAN: Final = 'gino.json_support.BooleanProperty'
JSON_OBJECT: Final = 'gino.json_support.ObjectProperty'
JSON_ARRAY: Final = 'gino.json_support.ArrayProperty'
JSON_NAMES: Final = {
    JSON_STRING,
    JSON_DATETIME,
    JSON_INTEGER,
    JSON_BOOLEAN,
    JSON_OBJECT,
    JSON_ARRAY,
}
