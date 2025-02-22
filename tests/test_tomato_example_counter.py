from tomato_example_counter import DriverInterface
from dgbowl_schemas.tomato.payload import Task
import time
import pytest
import pint

kwargs = dict(address="a", channel="1")


def test_create_device():
    interface = DriverInterface()
    print(f"{interface=}")
    ret = interface.dev_register(**kwargs)
    assert ret.success
    print(f"{interface.devmap=}")
    assert ("a", "1") in interface.devmap


def test_attr_wrong():
    interface = DriverInterface()
    ret = interface.dev_register(**kwargs)
    with pytest.raises(AssertionError, match="attr 'wrong'"):
        interface.dev_get_attr(attr="wrong", **kwargs)
    with pytest.raises(AssertionError, match="attr 'wrong'"):
        interface.dev_set_attr(attr="wrong", val="1.0", **kwargs)
    with pytest.raises(AssertionError, match="wrong dimensionality"):
        interface.dev_set_attr(attr="param", val="1.0 meter", **kwargs)
    with pytest.raises(AssertionError, match="smaller than"):
        interface.dev_set_attr(attr="param", val="0.05 s", **kwargs)


def test_get_attr():
    interface = DriverInterface()
    ret = interface.dev_register(**kwargs)
    ret = interface.dev_attrs(**kwargs)
    assert ret.success
    assert "min" in ret.data
    ret = interface.dev_get_attr(attr="min", **kwargs)
    assert ret.success
    assert ret.data == 0


def test_set_attr():
    interface = DriverInterface()
    interface.dev_register(**kwargs)

    ret = interface.dev_set_attr(attr="min", val=1.0, **kwargs)
    assert ret.success
    assert ret.data == 1.0

    ret = interface.dev_set_attr(attr="min", val=2, **kwargs)
    assert ret.success
    assert ret.data == 2.0

    ret = interface.dev_set_attr(attr="min", val="3", **kwargs)
    assert ret.success
    assert ret.data == 3.0

    ret = interface.dev_set_attr(attr="param", val="1.0", **kwargs)
    assert ret.success
    assert ret.data == pint.Quantity("1.0 second")

    ret = interface.dev_set_attr(attr="param", val="1.0 minute", **kwargs)
    assert ret.success
    assert ret.data == pint.Quantity("1.0 minute")


def test_task_random():
    interface = DriverInterface()
    interface.dev_register(**kwargs)
    task = Task(
        component_tag="a1",
        max_duration=1.0,
        sampling_interval=0.1,
        technique_name="random",
        technique_params={"min": 0, "max": 10},
    )
    ret = interface.task_start(task=task, **kwargs)
    assert ret.success

    ret = interface.dev_status(**kwargs)
    assert ret.success
    assert ret.data["running"]
    while ret.data["running"]:
        time.sleep(0.2)
        ret = interface.dev_status(**kwargs)
    ret = interface.task_data(**kwargs)
    assert ret.success
    print(f"{ret.data=}")
    assert ret.data.uts.shape == (10,)


def test_task_count():
    interface = DriverInterface()
    interface.dev_register(**kwargs)
    task = Task(
        component_tag="a1",
        max_duration=2.0,
        sampling_interval=0.1,
        technique_name="count",
        technique_params={"param": "3.0 seconds"},
    )
    ret = interface.task_start(task=task, **kwargs)
    assert ret.success

    ret = interface.dev_status(**kwargs)
    assert ret.success
    assert ret.data["running"]
    while ret.data["running"]:
        time.sleep(0.2)
        ret = interface.dev_status(**kwargs)
    ret = interface.task_data(**kwargs)
    assert ret.success
    print(f"{ret.data=}")
    assert ret.data.uts.shape == (20,)
