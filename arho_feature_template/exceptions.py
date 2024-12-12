class LayerNotFoundError(Exception):
    def __init__(self, layer_name: str):
        super().__init__(f"Layer {layer_name} not found")


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
