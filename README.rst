Falcon-Boilerplate
================

Falcon-Boilerplate is a simple no-thrills boilerplate for creating simple CRUD APIs
using `Falcon`_ and `SQLAlchemy`_ models.

.. _Falcon: https://falcon.readthedocs.io/en/stable/
.. _SQLAlchemy: https://www.sqlalchemy.org


Installing
----------

Install and update using `pip`_:

.. code-block:: text

  $ pip install -U git+https://github.com/sitzz/falcon-boilerplate.git

.. _pip: https://pip.pypa.io/en/stable/getting-started/


A Simple Example
----------------

.. code-block:: python

    from falcon import App
    from falcon_sqla import Manager
    from falcon_boilerplate.controller import Controller
    from falcon_boilerplate.router import ControllerRouter
    from falcon_boilerplate.sqlaman import sqla_manager
    from sqlalchemy import create_engine
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    manager = Manager(create_engine(config.db_uri))
    sqla_manager.manager = manager

    class UserModel(DeclarativeBase):
        __tablename__ = "user"
        id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
        username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)

    class UserRouter(ControllerRouter):
        base_path = '/user'
        version = 1

        def __init__(self, app):
            super().__init__(app, UserController(), logger=config.logger)

    class UserController(Controller):
        c = True
        r = True
        u = True
        model = UserModel

        def __init__(self):
            super().__init__()

    def create_app():
        app = App(
            cors_enable=True,
            middleware=middleware
        )

        # Attach routes from UserRouter
        UserRouter(app)

        return app

Documentation
-------------
Work in progress or something... Currently this repository is merely used by myself,
whether I will bother properly releasing to `Pypi`_ or create proper documentation
is somewhat up in the air.

If you like this repository please star it to let me know, or if you have any issues
or suggestions please create an issue `here on Github`_.

.. _Pypi: https://pypi.org
.. _here on Github: https://github.com/sitzz/falcon-boilerplate/issues/new/choose