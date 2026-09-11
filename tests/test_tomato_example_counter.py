import time

import pint
import pytest
from dgbowl_schemas.tomato.payload import Task

from tomato_example_counter import DriverInterface, SubModel

kwargs = {"address": "a", "channel": "1"}
NAME = "example_counter:a:1"
MODEL = SubModel(snum=5.0, sstr="t")


def test_create_teardown_device():
    interface = DriverInterface()
    print(f"{interface=}")
    ret = interface.cmp_register(name=NAME, **kwargs)
    assert ret.success
    print(f"{interface.devmap=}")
    assert NAME in interface.devmap
    ret = interface.cmp_quit(name=NAME)
    assert ret.success
    assert NAME not in interface.devmap


def test_attr_wrong():
    interface = DriverInterface()
    interface.cmp_register(name=NAME, **kwargs)
    with pytest.raises(ValueError, match="'min' cannot be None"):
        interface.cmp_set_attr(attr="min", val=None, name=NAME)
    with pytest.raises(ValueError, match="could not convert"):
        interface.cmp_set_attr(attr="min", val="wrong", name=NAME)
    with pytest.raises(AttributeError, match="unknown attr: 'wrong'"):
        interface.cmp_get_attr(attr="wrong", name=NAME)
    with pytest.raises(AttributeError, match="unknown attr: 'wrong'"):
        interface.cmp_set_attr(attr="wrong", val="1.0", name=NAME)
    with pytest.raises(ValueError, match="wrong dimensionality"):
        interface.cmp_set_attr(attr="param", val="1.0 meter", name=NAME)
    with pytest.raises(ValueError, match="smaller than"):
        interface.cmp_set_attr(attr="param", val="0.05 s", name=NAME)
    with pytest.raises(ValueError, match="'orange' is not in allowed options"):
        interface.cmp_set_attr(attr="choice", val="orange", name=NAME)


def test_get_attr():
    interface = DriverInterface()
    ret = interface.cmp_register(name=NAME, **kwargs)
    ret = interface.cmp_attrs(name=NAME)
    assert ret.success
    assert "min" in ret.data
    ret = interface.cmp_get_attr(attr="min", name=NAME)
    assert ret.success
    assert ret.data == 0


def test_set_attr():
    interface = DriverInterface()
    interface.cmp_register(name=NAME, **kwargs)

    ret = interface.cmp_set_attr(attr="min", val=1.0, name=NAME)
    assert ret.success
    assert ret.data == 1.0

    ret = interface.cmp_set_attr(attr="min", val=2, name=NAME)
    assert ret.success
    assert ret.data == 2.0

    ret = interface.cmp_set_attr(attr="min", val="3", name=NAME)
    assert ret.success
    assert ret.data == 3.0

    ret = interface.cmp_set_attr(attr="param", val="1.0", name=NAME)
    assert ret.success
    assert ret.data == pint.Quantity("1.0 second")

    ret = interface.cmp_set_attr(attr="param", val="1.0 minute", name=NAME)
    assert ret.success
    assert ret.data == pint.Quantity("1.0 minute")

    ret = interface.cmp_set_attr(attr="choice", val="blue", name=NAME)
    assert ret.success
    assert ret.data == "blue"

    ret = interface.cmp_get_attr(attr="model", name=NAME)
    assert ret.success
    assert ret.data is None

    ret = interface.cmp_set_attr(attr="model", val=MODEL, name=NAME)
    assert ret.success
    assert ret.data == MODEL

    ret = interface.cmp_get_attr(attr="model", name=NAME)
    assert ret.success
    assert ret.data == MODEL


def test_task_random():
    interface = DriverInterface()
    interface.cmp_register(name=NAME, **kwargs)
    task = Task(
        component_role="a1",
        max_duration=1.0,
        sampling_interval=0.1,
        technique_name="random",
        task_params={"min": 0, "max": 10},
    )
    ret = interface.task_start(task=task, name=NAME)
    print(f"{ret=}")
    assert ret.success
    time.sleep(0.2)

    ret = interface.cmp_status(name=NAME)
    print(f"{ret=}")
    assert ret.success
    assert ret.data.state == "task"
    while ret.data.state == "task":
        time.sleep(0.2)
        ret = interface.cmp_status(name=NAME)
    ret = interface.task_data(name=NAME)
    assert ret.success
    print(f"{ret.data=}")
    assert ret.data.uts.shape == (10,)
    assert ret.data["min"].shape == (10,)


def test_task_count():
    interface = DriverInterface()
    interface.cmp_register(name=NAME, **kwargs)
    task = Task(
        component_role="a1",
        max_duration=2.0,
        sampling_interval=0.1,
        technique_name="count",
        task_params={"param": "3.0 seconds", "model": MODEL},
    )
    ret = interface.task_start(task=task, name=NAME)
    print(f"{ret=}")
    assert ret.success
    time.sleep(0.2)

    ret = interface.cmp_status(name=NAME)
    print(f"{ret=}")
    assert ret.success
    assert ret.data.state == "task"
    while ret.data.state == "task":
        time.sleep(0.2)
        ret = interface.cmp_status(name=NAME)
    ret = interface.task_data(name=NAME)
    assert ret.success
    print(f"{ret.data=}")
    assert ret.data.uts.shape == (20,)
    assert ret.data["min"].shape == (20,)
    assert ret.data["model"].values[0] == MODEL.model_dump()

    ret = interface.cmp_last_data(name=NAME)
    print(f"{ret.data=}")
    assert ret.success
    assert ret.data["model"].values[0] == MODEL.model_dump()
