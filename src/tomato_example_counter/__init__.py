import logging
from tomato.driverinterface_2_0 import ModelInterface, ModelDevice, Attr
from dgbowl_schemas.tomato.payload import Task

from datetime import datetime
import math
import random
import time
import xarray as xr

logger = logging.getLogger(__name__)


class Device(ModelDevice):
    max: float
    min: float

    def __init__(self, driver, key, **kwargs):
        super().__init__(driver, key, **kwargs)
        self.constants["example_meta"] = "example string"
        self.min = 0
        self.max = 10

    def do_task(self, task: Task, t_start: float, t_now: float, **kwargs: dict) -> None:
        uts = datetime.now().timestamp()
        if task.technique_name == "count":
            data_vars = {
                "val": (["uts"], [math.floor(t_now - t_start)]),
            }
        elif task.technique_name == "random":
            data_vars = {
                "val": (["uts"], [random.uniform(self.min, self.max)]),
                "min": (["uts"], [self.min]),
                "max": (["uts"], [self.max]),
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
            "val": (["uts"], [random.uniform(self.min, self.max)]),
            "min": (["uts"], [self.min]),
            "max": (["uts"], [self.max]),
        }
        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [datetime.now().timestamp()])},
        )

    def set_attr(self, attr: str, val: float, **kwargs: dict) -> float:
        props = self.attrs()[attr]
        if not isinstance(val, props.type):
            val = props.type(val)
        if hasattr(self, attr):
            setattr(self, attr, val)
        return val

    def get_attr(self, attr: str, **kwargs: dict) -> float:
        if hasattr(self, attr):
            return getattr(self, attr)

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
