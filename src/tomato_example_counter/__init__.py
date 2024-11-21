import logging
from tomato.driverinterface_1_0 import ModelInterface, Attr
from dgbowl_schemas.tomato.payload import Task
from typing import Any

from datetime import datetime
import math
import random

logger = logging.getLogger(__name__)


class DriverInterface(ModelInterface):
    class DeviceManager(ModelInterface.DeviceManager):
        _max: float
        _min: float
        _val: float

        def __init__(self, driver, key, **kwargs):
            super().__init__(driver, key, **kwargs)
            self._min = 0.0
            self._max = 1.0

        def do_task(
            self, task: Task, t_start: float, t_now: float, **kwargs: dict
        ) -> None:
            uts = datetime.now().timestamp()
            if task.technique_name == "count":
                self._val = math.floor(t_now - t_start)
            elif task.technique_name == "random":
                self._val = random.uniform(self._min, self._max)
            self.data["uts"].append(uts)
            self.data["val"].append(self._val)

        def set_attr(self, attr: str, val: Any, **kwargs: dict) -> None:
            if attr == "max":
                self._max = val
            elif attr == "min":
                self._min = val

        def get_attr(self, attr: str, **kwargs: dict) -> Any:
            if hasattr(self, f"_{attr}"):
                return getattr(self, f"_{attr}")

        def attrs(self, **kwargs: dict) -> dict:
            return dict(
                val=Attr(type=int, status=True),
                max=Attr(type=float, rw=True, status=False),
                min=Attr(type=float, rw=True, status=False),
            )

        def capabilities(self, **kwargs: dict) -> set:
            return {"count", "random"}
