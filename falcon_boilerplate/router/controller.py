# pylint:disable=E0611

import json
import logging
from typing import Union

from falcon import App, HTTPInternalServerError, HTTPMethodNotAllowed, HTTPNotFound, Request, Response

from falcon_boilerplate.router import BaseRouter
from falcon_boilerplate.controller import Controller


class ControllerRouter(BaseRouter):
    def __init__(self, app: App, controller: Controller, logger: Union[logging.Logger, None] = None):
        super().__init__(app, logger)

        # Set controller for router
        self.controller = controller

        # Add endpoints. Support should be handled in the individual controller
        self.add_route("/", suffix="list")
        self.add_route("/{pk}")
        self.add_route("/")

    def on_post(self, req: Request, res: Response):
        """
        create a new record
        :param req: Request
        :param res: Response
        :return:
        """
        try:
            item = json.load(req.bounded_stream)
            if item and self.controller.create(item=item):
                res.status = 201
                res.text = "{}"
                return

            raise HTTPInternalServerError(description="unable to save record")
        except (HTTPMethodNotAllowed, HTTPNotFound) as _err:
            raise _err
        except Exception as _err:
            if isinstance(_err, HTTPInternalServerError):
                raise _err

            if self.logger is not None:
                self.logger.error(f"unhandled exception on_get ({type(_err).__name__}): {_err}")
        raise HTTPInternalServerError(description="unhandled exception in backend")

    def on_get(self, req: Request, res: Response, pk: Union[int, str]):
        """
        get a single record
        :param req: Request
        :param res: Response
        :param pk: primary key of record
        :return:
        """
        try:
            record = self.controller.read(pk=pk)
            res.text = json.dumps(record)
            return
        except (HTTPMethodNotAllowed, HTTPNotFound) as _err:
            raise _err
        except Exception as _err:
            if isinstance(_err, HTTPInternalServerError):
                raise _err

            if self.logger is not None:
                self.logger.error(f"unhandled exception on_get ({type(_err).__name__}): {_err}")
        raise HTTPInternalServerError(description="unhandled exception in backend")

    def on_get_list(self, req: Request, res: Response):
        """
        get a list of records
        :param req: Request
        :param res: Response
        :return:
        """
        try:
            records = self.controller.list()
            res.text = json.dumps(records)
            return
        except (HTTPMethodNotAllowed, HTTPNotFound) as _err:
            raise _err
        except Exception as _err:
            if isinstance(_err, HTTPInternalServerError):
                raise _err

            if self.logger is not None:
                self.logger.error(f"unhandled exception on_get ({type(_err).__name__}): {_err}")
        raise HTTPInternalServerError(description="unhandled exception in backend")

    def on_put(self, req: Request, res: Response, pk: Union[int, str]):
        """
        update a single record
        :param req: Request
        :param res: Response
        :param pk: primary key of record
        :return:
        """
        try:
            item = json.load(req.bounded_stream)
            if item and self.controller.update(pk=pk, item=item):
                res.status = 204
                res.text = ""
                return

            raise HTTPInternalServerError(description="unable to save record")
        except (HTTPMethodNotAllowed, HTTPNotFound) as _err:
            raise _err
        except Exception as _err:
            if isinstance(_err, HTTPInternalServerError):
                raise _err

            if self.logger is not None:
                self.logger.error(f"unhandled exception on_get ({type(_err).__name__}): {_err}")
        raise HTTPInternalServerError(description="unhandled exception in backend")

    def on_patch(self, req: Request, res: Response, pk: Union[int, str]):
        """
        update a partial single record. this will just call `on_get`
        :param req: Request
        :param res: Response
        :param pk: primary key of record
        :return:
        """
        self.on_put(req, res, pk)

    def on_delete(self, req: Request, res: Response, pk: Union[int, str]):
        """
        delete a single record
        :param req: Request
        :param res: Response
        :param pk: primary key of record
        :return:
        """
        try:
            if self.controller.delete(pk=pk):
                res.status = 204
                res.text = ""
                return

            raise HTTPInternalServerError(description="unable to delete record")
        except (HTTPMethodNotAllowed, HTTPNotFound) as _err:
            raise _err
        except Exception as _err:
            if isinstance(_err, HTTPInternalServerError):
                raise _err

            if self.logger is not None:
                self.logger.error(f"unhandled exception on_get ({type(_err).__name__}): {_err}")
        raise HTTPInternalServerError(description="unhandled exception in backend")
