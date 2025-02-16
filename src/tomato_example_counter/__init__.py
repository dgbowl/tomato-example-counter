import logging
from tomato.driverinterface_2_0 import ModelInterface, ModelDevice, Attr
from dgbowl_schemas.tomato.payload import Task
from typing import Any

from datetime import datetime
import math
import random
import time
import xarray as xr

logger = logging.getLogger(__name__)


class Device(ModelDevice):
    _max: float
    _min: float

    def __init__(self, driver, key, **kwargs):
        super().__init__(driver, key, **kwargs)
        self.constants["example_meta"] = "example string"
        self._min = 0
        self._max = 10

    def do_task(self, task: Task, t_start: float, t_now: float, **kwargs: dict) -> None:
        uts = datetime.now().timestamp()
        if task.technique_name == "count":
            data_vars = {
                "val": (["uts"], [math.floor(t_now - t_start)]),
            }
        elif task.technique_name == "random":
            data_vars = {
                "val": (["uts"], [random.uniform(self._min, self._max)]),
                "min": (["uts"], [self._min]),
                "max": (["uts"], [self._max]),
            }
        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [uts])},
        )
        if self.data is None:
            self.data = self.last_data
        else:
            self.data = xr.concat([self.data, self.last_data], dim="uts")

    def do_measure(self, **kwargs) -> None:
        data_vars = {
            "val": (["uts"], [random.uniform(self._min, self._max)]),
            "min": (["uts"], [self._min]),
            "max": (["uts"], [self._max]),
        }
        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [datetime.now().timestamp()])},
        )

    def set_attr(self, attr: str, val: Any, **kwargs: dict) -> None:
        if attr == "max":
            self._max = val if val is not None else 1.0
        elif attr == "min":
            self._min = val if val is not None else 0.0

    def get_attr(self, attr: str, **kwargs: dict) -> Any:
        if hasattr(self, f"_{attr}"):
            return getattr(self, f"_{attr}")

    def attrs(self, **kwargs: dict) -> dict:
        return dict(
            max=Attr(type=float, rw=True, status=False),
            min=Attr(type=float, rw=True, status=False),
        )

    def capabilities(self, **kwargs: dict) -> set:
        return {"count", "random"}


class DriverInterface(ModelInterface):
    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)


if __name__ == "__main__":
    kwargs = dict(address="a", channel=1)
    interface = DriverInterface()
    print(f"{interface=}")
    print(f"{interface.dev_register(**kwargs)=}")
    print(f"{interface.devmap=}")
    print(f"{interface.task_status(**kwargs)=}")
    print(f"{interface.dev_status(**kwargs)=}")
    task = Task(
        component_tag="a1",
        max_duration=5.0,
        sampling_interval=0.2,
        technique_name="random",
        technique_params={"min": 0, "max": 10},
    )
    print(f"{interface.task_start(**kwargs, task=task)=}")
    print(f"{interface.dev_status(**kwargs)=}")
    for i in range(0, 5):
        time.sleep(1)
        print(f"{interface.dev_get_attr(**kwargs, attr='val')=}")
        print(f"{interface.task_data(**kwargs)=}")
    print(f"{interface.dev_status(**kwargs)=}")
    task.technique_name = "count"
    print(f"{interface.task_start(**kwargs, task=task)=}")
    print(f"{interface.dev_status(**kwargs)=}")
    for i in range(0, 5):
        time.sleep(1)
        print(f"{interface.dev_get_attr(**kwargs, attr='val')=}")
        print(f"{interface.devmap[('a', 1)].status()=}")
        print(f"{interface.task_data(**kwargs)=}")
