from collections import namedtuple

ConfigurableField = namedtuple(
    "ConfigurableField",
    ["id", "name", "description", "annotation", "is_shared"],
    defaults=(None, None, None, False),
)
config = ConfigurableField()
print(config)
