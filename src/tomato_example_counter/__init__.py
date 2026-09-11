import logging
import math
import random
from datetime import UTC, datetime

import pint
import xarray as xr
from pydantic import BaseModel
from tomato.driverinterface_3_0 import (
    Attr,
    ModelComponent,
    ModelInterface,
    Status,
    Task,
)
from tomato.driverinterface_3_0.decorators import coerce_val
from tomato.driverinterface_3_0.types import Val

logger = logging.getLogger(__name__)

CHOICES = {"red", "blue", "green"}


class SubModel(BaseModel):
    snum: float
    sstr: str


class Component(ModelComponent):
    max: float
    min: float
    param: pint.Quantity
    choice: str
    model: SubModel | None

    def __init__(self, driver, name, **kwargs):
        super().__init__(driver, name, **kwargs)
        self.constants["example_meta"] = "example string"
        self.min = 0
        self.max = 10
        self.param = pint.Quantity("1.0 s")  # ty: ignore[invalid-assignment]
        self.choice = "green"
        self.model = None

    def do_task(
        self, task: Task, t_start: float, t_now: float, t_prev: float, **kwargs: dict
    ) -> None:
        uts = datetime.now(UTC).timestamp()
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
                data_vars[key] = (["uts"], [val.m], {"units": str(val.u)})  # ty: ignore[invalid-assignment]
            elif isinstance(val, SubModel):
                data_vars[key] = (["uts"], [val.model_dump()])
            else:
                data_vars[key] = (["uts"], [val])  # ty: ignore[invalid-assignment]
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
            elif isinstance(val, SubModel):
                data_vars[key] = (["uts"], [val.model_dump()])
            else:
                data_vars[key] = (["uts"], [val])

        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [datetime.now(UTC).timestamp()])},
        )

    @coerce_val
    def set_attr(self, attr: str, val: float, **kwargs: dict) -> Val:
        setattr(self, attr, val)
        return val

    def get_attr(self, attr: str, **kwargs: dict) -> Val:
        if not hasattr(self, attr):
            raise AttributeError(f"unknown attr: {attr!r}")
        return getattr(self, attr)

    def attrs(self, **kwargs: dict) -> dict:
        return {
            "max": Attr(type=float, rw=True, status=False),
            "min": Attr(type=float, rw=True, status=False),
            "param": Attr(
                type=pint.Quantity,
                rw=True,
                status=False,
                units="seconds",
                minimum=pint.Quantity("0.1 s"),
            ),
            "choice": Attr(
                type=str,
                rw=True,
                status=False,
                options=CHOICES,
            ),
            "model": Attr(
                type=SubModel,
                rw=True,
                status=False,
            ),
        }

    def capabilities(self, **kwargs: dict) -> set:
        return {"count", "random"}

    def quit(self, **kwargs):
        pass

    def status(self, **kwargs):
        attrs = {}
        for attr, props in self.attrs().items():
            if props.status:
                attrs[attr] = self.get_attr(attr)

        ret = Status(
            connected=True,
            state=self.state,  # ty: ignore[invalid-argument-type]
            can_submit=not self.task_list.full(),
            attrs=attrs,
        )
        return ret


class DriverInterface(ModelInterface):
    pass
