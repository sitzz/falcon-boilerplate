import falcon_sqla

__version__ = "0.2.0"

_sqla_manager: falcon_sqla.Manager = None


class _SqlaManager:
    @property
    def manager(self):
        return _sqla_manager

    @manager.setter
    def manager(self, manager):
        global _sqla_manager
        _sqla_manager = manager


sqla_manager = _SqlaManager()
