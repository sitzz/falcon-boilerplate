# pylint:disable=E0611

from datetime import datetime
import enum
import logging
from typing import Any, Dict, List, Union
from math import ceil

from falcon.errors import HTTPInternalServerError, HTTPBadRequest, HTTPMethodNotAllowed, HTTPNotFound
import falcon_sqla
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta, Query
from sqlalchemy.orm.collections import InstrumentedList

from falcon_boilerplate import sqla_manager
from falcon_boilerplate.exceptions import SqlaManagerRequired
from falcon_boilerplate.strfunc import camel_case_to_snake_case, lower_camel_case_it


class Controller:
    c = False  # Controller has create/write access
    r = False  # Controller has read access
    u = False  # Controller has update/write access
    d = False  # Controller has delete access
    model: DeclarativeMeta

    def __init__(self, *, manager: falcon_sqla.Manager = None, logger: Union[logging.Logger, None] = None,
                 timezone: str = "Etc/UTC"):
        # Add base instances and variables
        if manager is None:
            if sqla_manager.manager is None:
                raise SqlaManagerRequired("no SQLAlchemy manager available")

            manager = sqla_manager.manager

        self.session = manager.session_scope
        self.timezone = timezone
        self.pk = inspect(self.model).primary_key[0]

        # Add logger, if applicable
        self.logger = logger

    def create(self, item: dict) -> bool:
        """
        standard controller insert method
        :param item: dict
        new item defined as dict
        :return: bool
        :raises: HTTPInternalServerError
        """
        if self.model is None:
            self.logger.error(f"model not set for {self.__class__.__name__}")
            raise HTTPInternalServerError(description="an internal errors occurred")

        if not self.supports("create"):
            raise HTTPMethodNotAllowed(allowed_methods=self.supported, description="create action not supported")

        new_item = {}
        for k, v in item.items():
            k = camel_case_to_snake_case(k)

            # Only set attributes that the model actually has
            if not hasattr(self.model, k):
                continue

            # Don't allow setting certain columns, regardless
            if k == self.pk.name:
                continue

            # Check if the model has defined what can be set
            if hasattr(self.model, "__setable__") and k not in self.model.__setable__:
                raise HTTPBadRequest(description=f"not allowed to set field {k}")

            new_item[k] = v

        if hasattr(self, "required"):
            for field in self.required:
                if field not in new_item:
                    missing_fields = " & ".join(", ".join(self.required).rsplit(", ", maxsplit=1))
                    raise HTTPBadRequest(description=f"missing one or more fields, body must contain {missing_fields}")

        try:
            with self.session() as session:
                session.add(self.model(**new_item))
                session.commit()
                return True
        except Exception as _err:
            if self.logger is not None:
                self.logger.error(f"exception when creating item ({type(_err).__name__}): {_err}")
            raise HTTPInternalServerError(description="an unhandled error occurred when creating item")

    def read_single(self, pk: Union[int, str]) -> Union[Dict[Any, Any], None]:
        """
        standard controller read method, returns a single record from primary key
        :param pk: int | str
        primary key of a record
        :return: Dict
        :raises: HTTPInternalServerError
        """
        if self.model is None:
            self.logger.error(f"model not set for {self.__class__.__name__}")
            raise HTTPInternalServerError(description="an internal errors occurred")

        if not self.supports("read"):
            if self.logger is not None:
                self.logger.debug(f"read not supported, only supports {self.supported}")
            raise HTTPMethodNotAllowed(allowed_methods=self.supported,
                                       description="read (single) action not supported")

        with self.session() as session:
            if hasattr(self.model, "deleted_at"):
                row = session.query(self.model).filter(
                    self.pk == pk, self.model.deleted_at == None).one_or_none()  # noqa: E711
            else:
                row = session.get(self.model, pk)
            if not row:
                raise HTTPNotFound(description="item not found")

            session.expunge(row)
            row = self._to_dict(row)

            if hasattr(self, "filter"):
                row = self.filter(row)

        return row

    def read_list(self, page: int = 1, size: int = 10) -> Union[List[Dict[Any, Any]], None]:
        """
        standard controller read method, returns a list of records
        :param page: int
        :param size: int
        :return: List[Dict]
        """
        if self.model is None:
            self.logger.error(f"model not set for {self.__class__.__name__}")
            raise HTTPInternalServerError(description="an internal errors occurred")

        if not self.supports('read'):
            raise HTTPMethodNotAllowed(allowed_methods=self.supported, description='read (list) action not supported')

        ret = []
        with self.session() as session:
            query = session.query(self.model)
            if hasattr(self.model, "deleted_at"):
                query = query.filter(self.model.deleted_at == None)  # noqa: E711
            offset = (max(page - 1, 0)) * size
            rows = query.offset(offset).limit(size)
            for row in rows:
                row = self._to_dict(row)
                if hasattr(self, "filter"):
                    row = self.filter(row)
                ret.append(row)

        return ret

    def update(self, pk: Union[int, str], item: Dict[Any, Any]) -> bool:
        """
        standard controller update method, updates a single record from primary key
        :param pk: int | str
        primary key of a record
        :param item: Dict[Any, Any]
        :return: bool
        :raises: HTTPInternalServerError
        """
        if self.model is None:
            self.logger.error(f"model not set for {self.__class__.__name__}")
            raise HTTPInternalServerError(description="an internal errors occurred")

        if not self.supports("update"):
            raise HTTPMethodNotAllowed(allowed_methods=self.supported, description="update action not supported")

        try:
            with self.session() as session:
                row = session.get(self.model, pk)

                if not row:
                    raise HTTPNotFound(description="item not found")

                for k, v in item.items():
                    # We expect json formatted item names, we convert them to snake case
                    k = camel_case_to_snake_case(k)

                    # Only update attributes that the model actually has
                    if not hasattr(self.model, k):
                        continue

                    # Don't allow updating certain columns
                    if k == self.pk.name:
                        continue

                    # Check if the model has defined what can be updated
                    if hasattr(self.model, "__editable__") and k not in self.model.__editable__:
                        continue

                    setattr(row, k, v)

                session.commit()

            return True
        except Exception as _err:
            if self.logger is not None:
                self.logger.error(f"exception when updating item ({type(_err).__name__}): {_err}")
            raise HTTPInternalServerError(description="an unhandled error occurred when updating item")

    def delete(self, pk: Union[int, str]) -> bool:
        """
        standard controller delete method, deletes a single record from primary key.
        :param pk: int | str
        primary key of a record
        :return: bool
        :raises: HTTPInternalServerError
        """
        if self.model is None:
            self.logger.error(f"model not set for {self.__class__.__name__}")
            raise HTTPInternalServerError(description="an internal errors occurred")

        if not self.supports("delete"):
            raise HTTPMethodNotAllowed(allowed_methods=self.supported, description="delete action not supported")

        try:
            with self.session() as session:
                row = session.get(self.model, pk)

                if not row:
                    raise HTTPNotFound(description="item not found")

                session.delete(row)
                session.commit()

            return True
        except Exception as _err:
            if self.logger is not None:
                self.logger.error(f"exception when delete item ({type(_err).__name__}): {_err}")
            raise HTTPInternalServerError(description="an unhandled error occurred when updating item")

    def paginated_object(self, query: Union[Query, None] = None, total: int = 0, page: int = 1,
                         size: int = 1) -> dict:
        """
        return pagination objects
        :param query: SQLAlchemy ORM query object
        :param total: int
        :param page: int
        :param size: int
        :return: dict
        """
        ret: Dict[str, Any] = {}

        if query is None and total == 0:
            if self.logger is not None:
                self.logger.debug("query is None and total == 0")
            return ret

        if query is not None and not isinstance(query, Query):
            return ret

        if query is not None:
            total = query.count()

        pages = int(ceil(total / size))
        next_ = page + 1 if page < pages else None
        previous = page - 1 if 1 < page <= pages else None
        ret = {
            "size": size,
            "total": total,
            "pages": pages,
            "next": next_,
            "previous": previous
        }

        return ret

    def supports(self, action) -> bool:
        """
        method to determine controller abilities (create/write, read, update/write, delete)
        :param action: str
        one of create, read, update, delete

        :return: bool
        """
        return getattr(self, action[:1].lower(), False)

    @property
    def supported(self) -> List[str]:
        """
        returns a list methods allowed by this controller
        :return:
        """
        ret = ["HEAD", "OPTIONS"]
        for action, method in {"create": "POST", "read": "GET", "update": "PUT", "delete": "DELETE"}.items():
            if self.supports(action):
                ret.append(method)

        return ret

    @staticmethod
    def _sorted(item: dict) -> dict:
        """
        sort a dict by key
        :param item: dict
        :return: dict
        """
        return dict(sorted(item.items()))

    def _to_dict(self, item):
        """
        transform model object into a dict
        :param item: model object
        :return: dict
        """
        if isinstance(item, tuple):
            item = item[0]

        try:
            ret = {}
            for k in item.__table__.columns:
                v = getattr(item, k.name)

                if isinstance(v, InstrumentedList):
                    ret[k] = []
                    for item in v:
                        ret[k].append(item.id)
                    continue

                if isinstance(v, enum.Enum):
                    v = [
                        v.value,
                        v.name
                    ]

                if isinstance(v, datetime):
                    v = v.isoformat()

                key = lower_camel_case_it(k.name)
                ret[key] = v
            ret = self._sorted(ret)
        except Exception as _err:
            if self.logger is not None:
                self.logger.error(f"controller.to_dict: unhandled exception ({type(_err).__name__}): {_err}")
            ret = item

        return ret
