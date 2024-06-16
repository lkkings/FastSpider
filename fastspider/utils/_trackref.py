# -*- coding: utf-8 -*-
"""
@Description: 特定类跟踪工具
@Date       : 2024/6/15 23:00
@Author     : lkkings
@FileName:  : _trackref.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :
该模块提供了一些用于记录和报告的函数和类
对活动对象实例的引用。

如果要跟踪特定类的活动对象，只需
子类（而不是对象）object_ref。

关于性能：启用此库时对性能的影响最小，
并且在禁用时根本没有性能损失（因为object_ref只是一个
在这种情况下，别名表示反对）。
"""


from collections import defaultdict
from operator import itemgetter
from time import time
from typing import TYPE_CHECKING, Any, DefaultDict, Iterable
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self


NoneType = type(None)
live_refs: DefaultDict[type, WeakKeyDictionary] = defaultdict(WeakKeyDictionary)


class object_ref:
    """Inherit from this class to a keep a record of live instances"""

    __slots__ = ()

    def __new__(cls, *args: Any, **kwargs: Any) -> "Self":
        obj = object.__new__(cls)
        live_refs[cls][obj] = time()
        return obj


# using Any as it's hard to type type(None)
def format_live_refs(ignore: Any = NoneType) -> str:
    """Return a tabular representation of tracked objects"""
    s = "Live References\n\n"
    now = time()
    for cls, wdict in sorted(live_refs.items(), key=lambda x: x[0].__name__):
        if not wdict:
            continue
        if issubclass(cls, ignore):
            continue
        oldest = min(wdict.values())
        s += f"{cls.__name__:<30} {len(wdict):6}   oldest: {int(now - oldest)}s ago\n"
    return s


def print_live_refs(*a: Any, **kw: Any) -> None:
    """Print tracked objects"""
    print(format_live_refs(*a, **kw))


def get_oldest(class_name: str) -> Any:
    """Get the oldest object for a specific class name"""
    for cls, wdict in live_refs.items():
        if cls.__name__ == class_name:
            if not wdict:
                break
            return min(wdict.items(), key=itemgetter(1))[0]


def iter_all(class_name: str) -> Iterable[Any]:
    """Iterate over all objects of the same class by its class name"""
    for cls, wdict in live_refs.items():
        if cls.__name__ == class_name:
            return wdict.keys()
    return []

