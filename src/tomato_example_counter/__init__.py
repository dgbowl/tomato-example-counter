import logging
from tomato.driverinterface_1_0 import ModelInterface
from dgbowl_schemas.tomato.payload import Task

import time
import math
import random

logger = logging.getLogger(__name__)


class DriverInterface(ModelInterface):
    class DeviceInterface(ModelInterface.DeviceInterface):
        def task_runner(self, task, thread):
            t0 = time.perf_counter()
            tD = t0
            started = True
            self.data = []
            while getattr(thread, "do_run"):
                tN = time.perf_counter()
                if task.technique_name == "count":
                    val = math.floor(tN - t0)
                elif task.technique_name == "random":
                    val = random.uniform(
                        task.technique_params.get("min", 0),
                        task.technique_params.get("max", 1),
                    )
                self.status = dict(val=val, started=started)
                if tN - tD > task.sampling_interval:
                    self.data.append(dict(uts=tN, val=val))
                    tD += task.sampling_interval
                if tN - t0 > task.max_duration:
                    break
                time.sleep(max(1e-2, task.sampling_interval / 10))

    def attrs(self, **kwargs) -> dict:
        return dict(
            started=self.Attr(type=bool, rw=True, status=True),
            val=self.Attr(type=int, status=True),
        )

    def tasks(self, **kwargs) -> dict:
        return dict(
            count=dict(),
            random=dict(
                min=dict(type=float),
                max=dict(type=float),
            ),
        )


if __name__ == "__main__":
    kwargs = dict(address="a", channel=1)
    interface = DriverInterface()
    print(f"{interface=}")
    print(f"{interface.dev_register(**kwargs)=}")
    print(f"{interface.devmap=}")
    print(f"{interface.task_status(**kwargs)=}")
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
        print(f"{interface.task_data(**kwargs)=}")
