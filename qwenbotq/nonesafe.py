from __future__ import annotations

from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from typing import Any, NoReturn, overload

# ---------------------------------------------------------------------------
# 哨兵对象
# ---------------------------------------------------------------------------


class _NoneLike:
    """None 安全的哨兵对象：字符串化返回 ``"None"``，支持任意链式访问，布尔值为假。"""

    __slots__ = ()

    # ----- 链式访问 / 调用 ------------------------------------------------

    def __getattr__(self, _name: str) -> _NoneLike:
        # 对调试器/序列化等场景常见的 dunder 属性，保持标准语义：不存在就抛 AttributeError。
        # 否则像 debugpy 这类工具在变量展开时可能拿到错误类型并触发异常。
        if _name.startswith("__") and _name.endswith("__"):
            raise AttributeError(_name)
        return self

    def __getitem__(self, _key: Any) -> _NoneLike:
        return self

    def __call__(self, *_args: Any, **_kwargs: Any) -> _NoneLike:
        return self

    # ----- 容器协议 --------------------------------------------------------

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __len__(self) -> int:
        return 0

    def __contains__(self, _item: Any) -> bool:
        return False

    def __reversed__(self) -> Iterator[Any]:
        return iter(())

    # ----- dict 方法 -------------------------------------------------------

    def get(self, _key: Any, _default: Any = None) -> _NoneLike:
        return self

    def keys(self) -> KeysView[Any]:
        return {}.keys()

    def values(self) -> ValuesView:
        return {}.values()

    def items(self) -> ItemsView[Any, Any]:
        return {}.items()

    def pop(self, _key: Any, _default: Any = None) -> _NoneLike:
        return self

    def popitem(self) -> _NoneLike:
        return self

    def setdefault(self, _key: Any, _default: Any = None) -> _NoneLike:
        return self

    # ----- list 方法 -------------------------------------------------------

    def index(self, _value: Any, _start: Any = None, _stop: Any = None) -> NoReturn:
        raise ValueError("NoneLike object - value not found")

    def count(self, _value: Any) -> int:
        return 0

    def pop_list(self, _index: int = -1) -> _NoneLike:
        """list.pop 对应（避免与 dict.pop 冲突）。"""
        return self

    # ----- 运算符 / 内建 ---------------------------------------------------

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        return other is None or isinstance(other, _NoneLike)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(None)

    def __str__(self) -> str:
        return "None"

    def __repr__(self) -> str:
        return "None"

    def __neg__(self) -> _NoneLike:
        return self

    def __pos__(self) -> _NoneLike:
        return self

    def __abs__(self) -> _NoneLike:
        return self

    def __invert__(self) -> _NoneLike:
        return self

    # 数值运算（全部返回自身，避免 NoneType 运算抛异常）
    def __add__(self, _other: Any) -> _NoneLike:
        return self

    def __radd__(self, _other: Any) -> _NoneLike:
        return self

    def __sub__(self, _other: Any) -> _NoneLike:
        return self

    def __rsub__(self, _other: Any) -> _NoneLike:
        return self

    def __mul__(self, _other: Any) -> _NoneLike:
        return self

    def __rmul__(self, _other: Any) -> _NoneLike:
        return self

    def __truediv__(self, _other: Any) -> _NoneLike:
        return self

    def __rtruediv__(self, _other: Any) -> _NoneLike:
        return self

    def __floordiv__(self, _other: Any) -> _NoneLike:
        return self

    def __rfloordiv__(self, _other: Any) -> _NoneLike:
        return self

    def __mod__(self, _other: Any) -> _NoneLike:
        return self

    def __rmod__(self, _other: Any) -> _NoneLike:
        return self

    def __pow__(self, _other: Any) -> _NoneLike:
        return self

    def __rpow__(self, _other: Any) -> _NoneLike:
        return self

    # 比较运算
    def __lt__(self, _other: Any) -> bool:
        return False

    def __le__(self, _other: Any) -> bool:
        return False

    def __gt__(self, _other: Any) -> bool:
        return False

    def __ge__(self, _other: Any) -> bool:
        return False


NONE_LIKE = _NoneLike()


# ---------------------------------------------------------------------------
# 包装辅助
# ---------------------------------------------------------------------------


def _wrap(value: Any) -> Any:
    """将 None / 容器包装为 None 安全形式，其它类型原样返回。"""
    if value is None:
        return NONE_LIKE
    if isinstance(value, (NoneSafeDict, NoneSafeList, _NoneLike)):
        return value
    if isinstance(value, dict):
        return NoneSafeDict(value)
    if isinstance(value, list):
        return NoneSafeList(value)
    return value


# ---------------------------------------------------------------------------
# NoneSafeDict
# ---------------------------------------------------------------------------


class NoneSafeDict(dict):
    """None 安全的 dict。

    访问不存在的键返回 ``NONE_LIKE`` 而非抛出 ``KeyError``；
    值中包含的 dict / list 也会被自动包装。
    """

    # ---- 读 ---------------------------------------------------------------

    def __getitem__(self, key: Any) -> Any:
        if key not in self:
            return NONE_LIKE
        return _wrap(super().__getitem__(key))

    def get(self, key: Any, default: Any = None) -> Any:
        if key not in self:
            return NONE_LIKE if default is None else _wrap(default)
        return _wrap(super().get(key))

    # ---- 迭代相关 ----------------------------------------------------------

    def values(self) -> ValuesView:
        """返回迭代时自动包装每个 value 的视图。"""
        return _WrappedValuesView(self)

    def items(self) -> ItemsView[Any, Any]:
        """返回迭代时自动包装每个 value 的视图（key 不变）。"""
        return _WrappedItemsView(self)

    # keys() 无需覆盖 — key 不需要包装

    def __iter__(self) -> Iterator[Any]:
        return super().__iter__()  # 遍历 key，不需要包装

    def iterkeys(self) -> Iterator[Any]:
        """显式 key 迭代接口。"""
        return iter(self.keys())

    def itervalues(self) -> Iterator[Any]:
        """显式 value 迭代接口（自动包装）。"""
        return iter(self.values())

    def iteritems(self) -> Iterator[tuple[Any, Any]]:
        """显式 items 迭代接口（value 自动包装）。"""
        return iter(self.items())

    def __reversed__(self) -> Iterator[Any]:
        return reversed(list(self.keys()))  # py3.8+

    # ---- 写（返回值也做包装） ----------------------------------------------

    def pop(self, key: Any, default: Any = NONE_LIKE) -> Any:
        sentinel = object()
        if default is NONE_LIKE:
            v = super().pop(key, sentinel)
            if v is sentinel:
                return NONE_LIKE
            return _wrap(v)
        try:
            return _wrap(super().pop(key))
        except KeyError:
            return _wrap(default)

    def popitem(self) -> tuple[Any, Any] | _NoneLike:
        try:
            k, v = super().popitem()
            return k, _wrap(v)
        except KeyError:
            return NONE_LIKE

    def setdefault(self, key: Any, default: Any = None) -> Any:
        return _wrap(super().setdefault(key, default))

    # ---- 复制 --------------------------------------------------------------

    def copy(self) -> NoneSafeDict:
        return NoneSafeDict(self)

    # ---- 取值辅助（避免拿到原生 dict/list/None） -----------------------------

    def unwrap_or(self, key: Any, default: Any = None) -> Any:
        """安全读取：缺失键返回包装后的 default。"""
        return self.get(key, default)

    def first(self, default: Any = None) -> Any:
        """返回第一个 value（自动包装），空 dict 返回包装后的 default。"""
        for value in self.values():
            return value
        return NONE_LIKE if default is None else _wrap(default)

    # ---- 合并运算符 (py3.9+) -----------------------------------------------

    def __or__(self, other: Any) -> NoneSafeDict:
        return NoneSafeDict(super().__or__(other))

    def __ror__(self, other: Any) -> NoneSafeDict:
        return NoneSafeDict(super().__ror__(other))

    def __ior__(self, other: Any) -> NoneSafeDict:
        super().__ior__(other)
        return self


# ---------------------------------------------------------------------------
# NoneSafeList
# ---------------------------------------------------------------------------


class NoneSafeList(list):
    """None 安全的 list。

    越界 / 非法下标返回 ``NONE_LIKE``；内部 dict / list 自动包装。
    """

    # ---- 读 ---------------------------------------------------------------

    @overload
    def __getitem__(self, index: int) -> Any: ...
    @overload
    def __getitem__(self, index: slice) -> NoneSafeList: ...

    def __getitem__(self, index: Any) -> Any:
        try:
            value = super().__getitem__(index)
        except (IndexError, TypeError):
            return NONE_LIKE

        if isinstance(index, slice):
            return NoneSafeList(value)
        return _wrap(value)

    # ---- 迭代 --------------------------------------------------------------

    def __iter__(self) -> Iterator[Any]:
        """迭代时自动包装每一项。"""
        return (_wrap(v) for v in super().__iter__())

    def __reversed__(self) -> Iterator[Any]:
        return (_wrap(v) for v in super().__reversed__())

    # ---- 写（返回值包装） --------------------------------------------------

    def pop(self, index: int = -1) -> Any:  # type: ignore[override]
        try:
            return _wrap(super().pop(index))
        except IndexError:
            return NONE_LIKE

    # ---- 复制 --------------------------------------------------------------

    def copy(self) -> NoneSafeList:
        return NoneSafeList(self)

    # ---- 取值辅助（避免拿到原生 dict/list/None） -----------------------------

    def first(self, default: Any = None) -> Any:
        """返回首项（自动包装），空列表返回包装后的 default。"""
        if not self:
            return NONE_LIKE if default is None else _wrap(default)
        return _wrap(super().__getitem__(0))

    def last(self, default: Any = None) -> Any:
        """返回末项（自动包装），空列表返回包装后的 default。"""
        if not self:
            return NONE_LIKE if default is None else _wrap(default)
        return _wrap(super().__getitem__(-1))


# ---------------------------------------------------------------------------
# 视图包装（values / items）
# ---------------------------------------------------------------------------


class _WrappedValuesView(ValuesView):
    """迭代时自动包装每个 value 的 ValuesView。"""

    def __iter__(self) -> Iterator[Any]:
        return (_wrap(v) for v in self._mapping.values())

    def __contains__(self, value: Any) -> bool:
        return value in self._mapping.values()

    def __len__(self) -> int:
        return len(self._mapping)


class _WrappedItemsView(ItemsView):
    """迭代时只包装 value，保留 key 不变的 ItemsView。"""

    def __iter__(self) -> Iterator[tuple[Any, Any]]:
        return ((k, _wrap(v)) for k, v in self._mapping.items())

    def __contains__(self, item: Any) -> bool:
        return item in self._mapping.items()

    def __len__(self) -> int:
        return len(self._mapping)
