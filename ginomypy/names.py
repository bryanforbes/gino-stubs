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
