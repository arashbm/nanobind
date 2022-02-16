import test_classes_ext as t
import pytest
import gc

def test01_signature():
    assert t.Struct.__init__.__doc__ == (
        "__init__(*args, **kwargs) -> Any\n"
        "Overloaded function.\n"
        "\n"
        "1. __init__(self) -> None\n"
        "2. __init__(self, arg0: int) -> None")

    assert t.Struct.value.__doc__ == "value(self) -> int"
    assert t.Struct.create_move.__doc__ == "create_move() -> test_classes_ext.Struct"
    assert t.Struct.set_value.__doc__ == "set_value(self, value: int) -> None"


def test02_instantiate():
    gc.collect()
    t.reset()

    s1 = t.Struct()
    assert s1.value() == 5
    s2 = t.Struct(10)
    assert s2.value() == 10
    del s1
    del s2
    gc.collect()

    assert t.stats() == {
        'default_constructed': 1,
        'value_constructed': 1,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 2
    }


def test03_double_init():
    s = t.Struct()
    with pytest.raises(RuntimeError) as excinfo:
        s.__init__()
    assert 'the __init__ method should only be called once!' in str(excinfo.value)


def test04_rv_policy():
    gc.collect()
    t.reset()
    s = t.Struct()
    assert s.self() is s
    assert s.none() is None
    del s
    gc.collect()
    assert t.stats() == {
        'default_constructed': 1,
        'value_constructed': 0,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 1
    }

    # ------

    t.reset()
    assert t.Struct.create_take().value() == 10
    gc.collect()
    assert t.stats() == {
        'default_constructed': 0,
        'value_constructed': 1,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 1
    }

    # ------

    t.reset()
    assert t.Struct.create_move().value() == 11
    gc.collect()
    assert t.stats() == {
        'default_constructed': 0,
        'value_constructed': 1,
        'copy_constructed': 0,
        'move_constructed': 1,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 2
    }

    # ------

    t.reset()
    assert t.Struct.create_reference().value() == 12
    gc.collect()
    assert t.stats() == {
        'default_constructed': 0,
        'value_constructed': 0,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 0
    }

    # ------

    t.reset()
    assert t.Struct.create_copy().value() == 12
    gc.collect()
    assert t.stats() == {
        'default_constructed': 0,
        'value_constructed': 0,
        'copy_constructed': 1,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 1
    }

def test05_reference_internal():
    gc.collect()
    t.reset()
    s = t.PairStruct()
    s1 = s.s1
    s2 = s.s2
    del s
    assert t.stats() == {
        'default_constructed': 2,
        'value_constructed': 0,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 0
    }
    assert s2.value() == 5
    del s2
    gc.collect()

    assert t.stats() == {
        'default_constructed': 2,
        'value_constructed': 0,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 0
    }

    assert s1.value() == 5
    del s1
    gc.collect()

    assert t.stats() == {
        'default_constructed': 2,
        'value_constructed': 0,
        'copy_constructed': 0,
        'move_constructed': 0,
        'copy_assigned': 0,
        'move_assigned': 0,
        'destructed': 2
    }


def test06_big():
    x = [t.Big() for i in range(1024)]
    x = [t.BigAligned() for i in range(1024)]


def test07_inheritance():
    dog = t.Dog('woof')
    cat = t.Cat('meow')
    assert isinstance(dog, t.Animal) and isinstance(dog, t.Dog)
    assert isinstance(cat, t.Animal) and isinstance(cat, t.Cat)
    assert t.go(dog) == 'Dog says woof'
    assert t.go(cat) == 'Cat says meow'


def test08_method_vectorcall():
    out = []

    def f(a, b, c, d, e):
        out.append((a, b, c, d, e))

    class my_class:
        def f(self, a, b, c, d, e):
            self.out = ((a, b, c, d, e))

    t.call_function(f)

    i = my_class()
    t.call_method(i)
    assert out == [(1, 2, "hello", True, 4)]
    assert i.out == (1, 2, "hello", True, 4)


def test09_inheritance_py():
    class Dachshund(t.Animal):
        def __init__(self):
            pass
            #  print("in init()")
            #  super().__init__()
            #  print("after init()")
        def type(self):
            print('in type()')
            return "Dachshund"
        def what(self):
            print('in what()')
            return "yap"

    d = Dachshund()
    #  assert t.go(d) == 'Dachshund says yap'