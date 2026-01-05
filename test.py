class Animal:
    def __init__(self, name):
        self.name = name


dog = Animal("小狗")

print(dog.__class__.__name__)
