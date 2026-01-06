from typing import Dict


def foo(a: dict[str, str]):
    print(a)


foo({"a": "123"})


def bar(b: Dict[str, str]):
    print(b)


bar({"name": "abc"})
