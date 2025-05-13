import logging
from tomato.driverinterface_2_1 import ModelInterface, ModelDevice, Attr
from tomato.driverinterface_2_1.types import Val
from tomato.driverinterface_2_1.decorators import coerce_val
from dgbowl_schemas.tomato.payload import Task

from datetime import datetime
import math
import random
import xarray as xr
import pint

logger = logging.getLogger(__name__)

CHOICES = {"red", "blue", "green"}


class Device(ModelDevice):
    max: float
    min: float
    param: pint.Quantity
    choice: str

    def __init__(self, driver, key, **kwargs):
        super().__init__(driver, key, **kwargs)
        self.constants["example_meta"] = "example string"
        self.min = 0
        self.max = 10
        self.param = pint.Quantity("1.0 s")
        self.choice = "green"

    def do_task(self, task: Task, t_start: float, t_now: float, **kwargs: dict) -> None:
        uts = datetime.now().timestamp()
        if task.technique_name == "count":
            data_vars = {
                "val": (["uts"], [math.floor(t_now - t_start)]),
            }
        elif task.technique_name == "random":
            data_vars = {
                "val": (["uts"], [random.uniform(self.min, self.max)]),
            }
        for key in self.attrs(**kwargs):
            val = self.get_attr(attr=key)
            if isinstance(val, pint.Quantity):
                data_vars[key] = (["uts"], [val.m], {"units": str(val.u)})
            else:
                data_vars[key] = (["uts"], [val])
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
        }
        for key in self.attrs(**kwargs):
            val = self.get_attr(attr=key)
            if isinstance(val, pint.Quantity):
                data_vars[key] = (["uts"], [val.m], {"units": str(val.u)})
            else:
                data_vars[key] = (["uts"], [val])

        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [datetime.now().timestamp()])},
        )

    @coerce_val
    def set_attr(self, attr: str, val: float, **kwargs: dict) -> Val:
        setattr(self, attr, val)
        return val

    def get_attr(self, attr: str, **kwargs: dict) -> Val:
        assert hasattr(self, attr), f"unknown attr: {attr!r}"
        return getattr(self, attr)

    def attrs(self, **kwargs: dict) -> dict:
        return dict(
            max=Attr(type=float, rw=True, status=False),
            min=Attr(type=float, rw=True, status=False),
            param=Attr(
                type=pint.Quantity,
                rw=True,
                status=False,
                units="seconds",
                minimum=pint.Quantity("0.1 s"),
            ),
            choice=Attr(
                type=str,
                rw=True,
                status=False,
                options=CHOICES,
            ),
        )

    def capabilities(self, **kwargs: dict) -> set:
        return {"count", "random"}


class DriverInterface(ModelInterface):
    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)
