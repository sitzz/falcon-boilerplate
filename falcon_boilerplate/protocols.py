from typing import Any, Dict, List, Protocol, Union


class Controller(Protocol):
    def create(self, item: Dict[Any, Any]) -> bool:
        pass

    def read_single(self, pk: Union[int, str]) -> Union[Dict[Any, Any], None]:
        pass

    def read_list(self, page: int = 1, size: int = 10) -> Union[List[Dict[Any, Any]], None]:
        pass

    def update(self, pk: Union[int, str], item: Dict[Any, Any]) -> bool:
        pass

    def delete(self, pk: Union[int, str]) -> bool:
        pass

    def supports(self, action: str) -> bool:
        pass

    @property
    def supported(self) -> List[str]:
        ...
