import contextlib
from pathlib import Path

from ._registry import register_behavior, register_preset


def _to_pascal(s: str) -> str:
    parts = [p for p in s.replace("-", "_").split("_") if p]
    return "".join(p.capitalize() for p in parts)


def _to_snake_lower(s: str) -> str:
    return s.replace("-", "_").lower()


def expose_entity(
    *,
    module_globals: dict,
    preset_cls: type,
    behavior_obj,
    register_strategy,
) -> tuple[str, str, str]:
    """
    Помещает preset_cls и behavior_obj в module_globals под корректными именами,
    берет базовое имя из override_name или из __file__ (module_globals['__file__']).
    Регистрирует через register_preset/register_behavior и дополняет __all__.
    Если передан register_strategy — также декорирует/регистрирует поведение там.
    """
    file_path = module_globals.get("__file__")
    assert file_path is not None, "__file__ not found in module_globals"
    stem = Path(file_path).stem
    export_name = _to_pascal(stem)
    instance_name = _to_snake_lower(stem)

    module_globals[export_name] = preset_cls

    if hasattr(preset_cls, "name"):
        with contextlib.suppress(Exception):
            preset_cls.name = instance_name

    beh_name = getattr(behavior_obj, "__name__", f"{instance_name}_ai")
    preferred_beh_name = f"{instance_name}_ai"
    module_globals.setdefault(preferred_beh_name, behavior_obj)
    module_globals.setdefault(beh_name, behavior_obj)

    if register_strategy:
        with contextlib.suppress(Exception):
            register_strategy(export_name)(behavior_obj)

    with contextlib.suppress(Exception):
        register_preset(export_name, preset_cls)
    with contextlib.suppress(Exception):
        register_behavior(export_name, behavior_obj)

    all_list = module_globals.get("__all__")
    if all_list is None:
        all_list = []
        module_globals["__all__"] = all_list
    if export_name not in all_list:
        all_list.append(export_name)

    return export_name, instance_name, preferred_beh_name
