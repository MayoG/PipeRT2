from abc import ABC, abstractmethod


class Rout(ABC):
    @abstractmethod
    def func(self):
        pass


class RoutImpl(Rout):
    @abstractmethod
    def extended_run(self):
        pass

    def func(self):
        pass


class FpsImpl(RoutImpl):
    @abstractmethod
    def extended_run(self):
        pass

    def func(self):
        print("In fps")
        self.extended_run()


class Src(RoutImpl):
    def extended_run(self):
        print("Src")


class Dst(RoutImpl):
    def extended_run(self):
        print("Dst")


src = Src()

src.__class__ = type(f'{Src.__name__}.{FpsImpl.__name__}', (Src, FpsImpl), {})

src.func()

print(src.__class__)


class Name(ABC):
    def get_name(self):
        pass


class Gentleman(Name):
    def introduce_self(self):
        return "Hello, my name is %s" % self.get_name()


class Person(Name):
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


p = Person("John")
p.__class__ = type('GentlePerson',(Person,Gentleman),{})
print(p.introduce_self())
# "Hello, my name is John"