import uuid

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.games.models import Game

from api.games.assets.models import Asset
from api.games.entities.models import Entity
from api.games.scenes.models import Scene


class LabelRegistry:
    def __init__(self):
        self._asset_labels: dict[uuid.UUID, str] = {}
        self._entity_labels: dict[uuid.UUID, str] = {}
        self._component_labels: dict[uuid.UUID, str] = {}

    def add_game(self, game: "Game"):
        """Add all labels for a game's scenes, assets, and entities."""
        self._add_scenes(game.scenes)
        self._add_assets(game.assets)
        self._add_entities(game.entities)

    def _add_scenes(self, scenes: list[Scene]):
        for scene in scenes:
            self._entity_labels[scene.id] = f"scene__{scene.name}"

    def _add_assets(self, assets: list[Asset]):
        for asset in assets:
            self._asset_labels[asset.id] = f"asset__{asset.type}__{asset.name}"

    def _add_entities(self, entities: list[Entity]):
        for entity in entities:
            self._entity_labels[entity.id] = f"entity__{entity.name}"
            # Add labels for all components attached to this entity
            for component in entity.components:
                self._component_labels[component.id] = f"component__{entity.name}__{component.name}"

    def get_scene_label(self, scene_id: uuid.UUID) -> str:
        if scene_id not in self._entity_labels:
            raise KeyError(f"Scene with ID {scene_id} not found in label registry.")
        return self._entity_labels[scene_id]

    def get_asset_label(self, asset_id: uuid.UUID) -> str:
        if asset_id not in self._asset_labels:
            raise KeyError(f"Asset with ID {asset_id} not found in label registry.")
        return self._asset_labels[asset_id]

    def get_entity_label(self, entity_id: uuid.UUID) -> str:
        if entity_id not in self._entity_labels:
            raise KeyError(f"Entity with ID {entity_id} not found in label registry.")
        return self._entity_labels[entity_id]

    def get_component_label(self, component_id: uuid.UUID) -> str:
        if component_id not in self._component_labels:
            raise KeyError(f"Component with ID {component_id} not found in label registry.")
        return self._component_labels[component_id]