from typing import TypedDict


class GCInputs(TypedDict, total=False):
    Left: bool
    Right: bool
    Down: bool
    Up: bool
    Z: bool
    R: bool
    L: bool
    A: bool
    B: bool
    X: bool
    Y: bool
    Start: bool
    StickX: int
    StickY: int
    CStickX: int
    CStickY: int
    TriggerLeft: int
    TriggerRight: int
    AnalogA: int
    AnalogB: int
    Connected: bool


class DolphinGCController:
    def __init__(self, controller, port=0):
        self._controller = controller
        self._port = port
        self._user_inputs = controller.get_gc_buttons(port)
    
    def current_inputs(self) -> GCInputs:
        return self._controller.get_gc_buttons(self._port)
    
    def user_inputs(self) -> GCInputs:
        return self._user_inputs

    def set_inputs(self, new_inputs: GCInputs):
        current_inputs = self._controller.get_gc_buttons(self._port)
        self._controller.set_gc_buttons(self._port, {**current_inputs, **new_inputs})


GC_STICK_RANGES = {
    7: (205, 255),
    6: (197, 204),
    5: (188, 196),
    4: (179, 187),
    3: (170, 178),
    2: (161, 169),
    1: (152, 160),
    0: (113, 151),
    -1: (105, 112),
    -2: (96, 104),
    -3: (87, 95),
    -4: (78, 86),
    -5: (69, 77),
    -6: (60, 68),
    -7: (0, 59),
}


def to_raw_gc_stick(mkw_stick: int):
    try:
        return GC_STICK_RANGES[mkw_stick][0]
    except KeyError:
        raise IndexError(f"Input ({mkw_stick}) outside of expected range (-7 to 7)")

def to_mkwii_gc_stick(raw_stick: int):
    for val, (start, end) in GC_STICK_RANGES.items():
        if start <= raw_stick <= end:
            return val
    raise IndexError(f"Input ({raw_stick}) outside of expected range (0 to 255)")


def convert_stick_inputs(inputs: GCInputs, mkwii_to_raw=False):
    for mkey in ("StickX", "StickY", "CStickX", "CStickY"):
        if mkey in inputs:
            if mkwii_to_raw:
                inputs[mkey] = to_raw_gc_stick(inputs[mkey])
            else:
                inputs[mkey] = to_mkwii_gc_stick(inputs[mkey])
    return inputs


class MKWiiGCController(DolphinGCController):
    def current_inputs(self) -> GCInputs:
        return convert_stick_inputs(super().current_inputs())
    
    def user_inputs(self) -> GCInputs:
        return convert_stick_inputs(super().current_inputs())

    def set_inputs(self, new_inputs: GCInputs):
        super().set_inputs(convert_stick_inputs(new_inputs, mkwii_to_raw=True))