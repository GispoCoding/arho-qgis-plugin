from __future__ import annotations


class LayerNotFoundError(Exception):
    def __init__(self, layer_name: str, group_name: str | None = None):
        in_group = f" in layer group '{group_name}'" if group_name else ""
        super().__init__(f"Layer {layer_name} not found{in_group}")


class LayerGroupNotFoundError(LayerNotFoundError):
    def __init__(self, group_name: str):
        # This is about the group, not a single layer, so bypass LayerNotFoundError.__init__
        Exception.__init__(self, f"Layer group '{group_name}' not found")


class LayerIoError(IOError): ...


class LayerEditableError(LayerIoError):
    def __init__(self, layer_name: str):
        super().__init__(f"Layer {layer_name} is editable, when it should not be.")


class UnsavedChangesError(LayerIoError):
    def __init__(self):
        super().__init__("Unsaved changes found")


class LayerNotVectorTypeError(Exception):
    def __init__(self, layer_name: str):
        super().__init__(f"Layer {layer_name} is not a vector layer")


class LayerNameNotFoundError(Exception):
    def __init__(self, layer_name: str):
        super().__init__(f"Layer {layer_name} not found")


class ConfigSyntaxError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Invalid config syntax: {message}")


class FeatureNotFoundError(Exception):
    def __init__(self, id_: str, layer_name: str):
        super().__init__(f"Feature with ID '{id_}' not found for layer {layer_name}")


class UnexpectedNoneError(Exception):
    """Internal QGIS errors that should not be happened"""


class NotPlanObjectLayerError(Exception):
    def __init__(self, layer_name: str):
        super().__init__(f"Layer {layer_name} is not a plan object layer")
