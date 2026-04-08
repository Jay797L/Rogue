from domain.base.core.pixel import Pixel
from domain.base.data.entities.player import Player
from domain.map.map_assembly.map_manager import MapManager
from domain.vision.ray_caster import RaycastingVisibility
from domain.vision.vision_memory_decorator import VisionMemoryDecorator
from domain.vision.vision_scoped import ScopedVision


class FogOfWarVision(ScopedVision):
    def __init__(self, map_manager: MapManager, character_of_view: Player):
        inner = ScopedVision(map_manager, character_of_view)
        inner._raycaster = RaycastingVisibility(map_manager)
        self._wrapped = VisionMemoryDecorator(inner)

    def __getattr__(self, name):

        return getattr(self._wrapped, name)

    def __dir__(self):

        return sorted(set(super().__dir__() + dir(self._wrapped)))

    def take_all(self):
        return self._wrapped.take_all()

    def __call__(self) -> list[Pixel]:
        return self._wrapped.take_all()
