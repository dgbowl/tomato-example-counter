import logging
from tomato.driverinterface_2_0 import ModelInterface, ModelDevice, Attr
from dgbowl_schemas.tomato.payload import Task

from datetime import datetime
import math
import random
import xarray as xr
import pint

logger = logging.getLogger(__name__)


class Device(ModelDevice):
    max: float
    min: float
    param: pint.Quantity

    def __init__(self, driver, key, **kwargs):
        super().__init__(driver, key, **kwargs)
        self.constants["example_meta"] = "example string"
        self.min = 0
        self.max = 10
        self.param = pint.Quantity("1.0 s")

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

    def set_attr(self, attr: str, val: float, **kwargs: dict) -> float:
        assert hasattr(self, attr), f"attr {attr!r} not present on component"
        props = self.attrs()[attr]
        if not isinstance(val, props.type):
            val = props.type(val)
        if isinstance(val, pint.Quantity):
            if val.dimensionless and props.units is not None:
                val = pint.Quantity(val.m, props.units)
            assert (
                val.dimensionality == getattr(self, attr).dimensionality
            ), f"attr {attr!r} has the wrong dimensionality {str(val.dimensionality)}"
        assert (
            props.minimum is None or val > props.minimum
        ), f"attr {attr!r} is smaller than {props.minimum}"
        assert (
            props.maximum is None or val < props.maximum
        ), f"attr {attr!r} is greater than {props.maximum}"

        setattr(self, attr, val)
        return val

    def get_attr(self, attr: str, **kwargs: dict) -> float:
        assert hasattr(self, attr), f"attr {attr!r} not present on component"
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
        )

    def capabilities(self, **kwargs: dict) -> set:
        return {"count", "random"}


class DriverInterface(ModelInterface):
    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)
