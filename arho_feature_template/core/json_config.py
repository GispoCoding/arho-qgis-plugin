from dataclasses import dataclass


@dataclass
class JsonKeys:
    VERSION = "version"
    NAME = "name"
    TEMPLATES = "templates"

    DESCRIPTION = "description"
    FEATURE = "feature"

    LAYER = "layer"
    FIELDS = "fields"
    CHILDREN = "children"

    FIELD = "field"
    VALUE = "value"
    MODIFIABLE = "allow_user_input"
    HIDDEN = "hidden"
    REQUIRED = "required"
