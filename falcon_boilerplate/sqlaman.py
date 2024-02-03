from typing import Union

import falcon_sqla

_sqla_manager: Union[falcon_sqla.Manager, None] = None


class _SqlaManager:
    @property
    def manager(self):
        return _sqla_manager

    @manager.setter
    def manager(self, manager):
        global _sqla_manager
        _sqla_manager = manager


sqla_manager = _SqlaManager()
