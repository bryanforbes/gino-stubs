from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Final  # noqa

COLUMN_NAME = 'sqlalchemy.sql.schema.Column'  # type: Final
GINO_NAME = 'gino.api.Gino'  # type: Final
DECLARATIVE_BASE_NAME = 'gino.declarative.declarative_base'  # type: Final
CRUD_CLASS_CREATE_NAME = 'gino.crud._CreateWithoutInstance.__call__'  # type: Final
CRUD_UPDATE_NAME = 'gino.crud._UpdateWithInstance.__call__'  # type: Final
CRUD_UPDATE_REQUEST_NAME = 'gino.crud.UpdateRequest.update'  # type: Final
VALUES_NAMES = {
    CRUD_CLASS_CREATE_NAME,
    CRUD_UPDATE_NAME,
    CRUD_UPDATE_REQUEST_NAME,
}  # type: Final
