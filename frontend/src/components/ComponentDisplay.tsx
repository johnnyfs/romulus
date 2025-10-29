import { useState, useEffect } from 'react';
import { Save, RefreshCw, Plus } from 'lucide-react';
import styles from './ComponentDisplay.module.css';
import type { GameGetResponse } from '../client/models/GameGetResponse';
import { ScenesService } from '../client/services/ScenesService';
// import { ComponentsService } from '../client/services/ComponentsService'; // DEPRECATED: Components replaced by Assets
import { EntitiesService } from '../client/services/EntitiesService';
import { getNESColor } from '../constants/nesColors';
import { getDefaultPalette } from '../constants/palettePresets';
import ColorPicker from './ColorPicker';
import PaletteEditor, { type PaletteData, type SubPalette } from './PaletteEditor';
import EntityEditor, { type EntityData } from './EntityEditor';
import ComponentSelector, { type ComponentType } from './ComponentSelector';

interface ComponentDisplayProps {
  game: GameGetResponse | null;
  onRebuildROM?: () => void;
  onSceneUpdated?: () => void;
}

interface SceneEdit {
  sceneId: string;
  backgroundColorIndex: number;
  backgroundPalette: string | null;
  spritePalette: string | null;
  isDirty: boolean;
}

function ComponentDisplay({ game, onRebuildROM, onSceneUpdated }: ComponentDisplayProps) {
  const [editingScenes, setEditingScenes] = useState<Map<string, SceneEdit>>(new Map());
  const [showColorPicker, setShowColorPicker] = useState<string | null>(null);
  const [colorPickerAnchor, setColorPickerAnchor] = useState<HTMLElement | null>(null);
  const [saving, setSaving] = useState<Set<string>>(new Set());
  const [scenePalettes, setScenePalettes] = useState<Map<string, Map<string, PaletteData>>>(new Map());
  const [paletteCounter, setPaletteCounter] = useState(0);
  const [sceneEntities, setSceneEntities] = useState<Map<string, Map<string, EntityData>>>(new Map());

  // Initialize scenePalettes from game.assets when game loads
  useEffect(() => {
    if (!game || !game.assets) return;

    const newScenePalettes = new Map<string, Map<string, PaletteData>>();

    // For each scene, find all palette assets
    game.scenes.forEach(scene => {
      const scenePaletteMap = new Map<string, PaletteData>();

      // Add all palette assets to this scene
      // Note: Currently assets are global, so we show them on all scenes
      game.assets.forEach(asset => {
        if (asset.type === 'palette' && asset.data.type === 'palette' && asset.data.palettes) {
          const paletteData: PaletteData = {
            id: asset.id,
            name: asset.name,
            subPalettes: asset.data.palettes.map(palette =>
              palette.colors.map(color => color.index) as SubPalette
            ) as [SubPalette, SubPalette, SubPalette, SubPalette],
            isDirty: false,
          };
          scenePaletteMap.set(asset.id, paletteData);
        }
      });

      if (scenePaletteMap.size > 0) {
        newScenePalettes.set(scene.id, scenePaletteMap);
      }
    });

    setScenePalettes(newScenePalettes);
  }, [game]);

  // Initialize sceneEntities from game.entities when game loads
  useEffect(() => {
    if (!game) return;

    const newSceneEntities = new Map<string, Map<string, EntityData>>();

    // Create a map of all game entities by ID for quick lookup
    const entitiesById = new Map(
      game.entities?.map(entity => [entity.id, entity]) || []
    );

    // For each scene, build a map of its referenced entities
    game.scenes.forEach(scene => {
      const sceneEntityMap = new Map<string, EntityData>();

      // scene.scene_data.entities is an array of entity UUIDs
      scene.scene_data.entities?.forEach(entityId => {
        const entity = entitiesById.get(entityId);
        if (entity) {
          const entityData: EntityData = {
            id: entity.id,
            name: entity.name,
            x: entity.entity_data.x,
            y: entity.entity_data.y,
            isDirty: false,
          };
          sceneEntityMap.set(entity.id, entityData);
        }
      });

      if (sceneEntityMap.size > 0) {
        newSceneEntities.set(scene.id, sceneEntityMap);
      }
    });

    setSceneEntities(newSceneEntities);
  }, [game]);

  const getSceneEdit = (sceneId: string, scene: any): SceneEdit => {
    return editingScenes.get(sceneId) || {
      sceneId,
      backgroundColorIndex: scene.scene_data.background_color.index,
      backgroundPalette: scene.scene_data.background_palettes || null,
      spritePalette: scene.scene_data.sprite_palettes || null,
      isDirty: false,
    };
  };

  const handleColorClick = (sceneId: string, event: React.MouseEvent<HTMLButtonElement>) => {
    setShowColorPicker(sceneId);
    setColorPickerAnchor(event.currentTarget);
  };

  const handleColorSelect = (sceneId: string, colorIndex: number) => {
    const scene = game?.scenes.find(s => s.id === sceneId);
    if (!scene) return;

    const currentEdit = getSceneEdit(sceneId, scene);
    const originalColorIndex = scene.scene_data.background_color.index;

    const newEditingScenes = new Map(editingScenes);
    newEditingScenes.set(sceneId, {
      ...currentEdit,
      backgroundColorIndex: colorIndex,
      isDirty: colorIndex !== originalColorIndex ||
               currentEdit.backgroundPalette !== (scene.scene_data.background_palettes || null) ||
               currentEdit.spritePalette !== (scene.scene_data.sprite_palettes || null),
    });
    setEditingScenes(newEditingScenes);
  };

  const handlePaletteSelect = (sceneId: string, paletteType: 'background' | 'sprite', paletteName: string | null) => {
    const scene = game?.scenes.find(s => s.id === sceneId);
    if (!scene) return;

    const currentEdit = getSceneEdit(sceneId, scene);
    const originalBgPalette = scene.scene_data.background_palettes || null;
    const originalSpritePalette = scene.scene_data.sprite_palettes || null;

    const newEdit = {
      ...currentEdit,
      [paletteType === 'background' ? 'backgroundPalette' : 'spritePalette']: paletteName,
    };

    const newEditingScenes = new Map(editingScenes);
    newEditingScenes.set(sceneId, {
      ...newEdit,
      isDirty: newEdit.backgroundColorIndex !== scene.scene_data.background_color.index ||
               newEdit.backgroundPalette !== originalBgPalette ||
               newEdit.spritePalette !== originalSpritePalette,
    });
    setEditingScenes(newEditingScenes);
  };

  const handleSaveScene = async (sceneId: string) => {
    if (!game) return;

    const scene = game.scenes.find(s => s.id === sceneId);
    const edit = editingScenes.get(sceneId);
    if (!scene || !edit || !edit.isDirty) return;

    setSaving(prev => new Set(prev).add(sceneId));

    try {
      await ScenesService.updateSceneGamesGameIdScenesSceneIdPut(
        game.id,
        sceneId,
        {
          scene_data: {
            ...scene.scene_data,
            background_color: { index: edit.backgroundColorIndex },
            background_palettes: edit.backgroundPalette,
            sprite_palettes: edit.spritePalette,
          },
        }
      );

      // Clear dirty state
      const newEditingScenes = new Map(editingScenes);
      newEditingScenes.delete(sceneId);
      setEditingScenes(newEditingScenes);

      // Notify parent
      if (onSceneUpdated) {
        onSceneUpdated();
      }
    } catch (error) {
      console.error('Failed to save scene:', error);
      alert('Failed to save scene');
    } finally {
      setSaving(prev => {
        const newSet = new Set(prev);
        newSet.delete(sceneId);
        return newSet;
      });
    }
  };

  const handleSaveAll = async () => {
    if (!game) return;

    const dirtyScenes = Array.from(editingScenes.values()).filter(edit => edit.isDirty);

    if (dirtyScenes.length === 0) return;

    // Save all dirty scenes in parallel
    await Promise.all(dirtyScenes.map(edit => handleSaveScene(edit.sceneId)));
  };

  const handleRebuildROMClick = async () => {
    // Save all changes first, then rebuild
    await handleSaveAll();
    if (onRebuildROM) {
      onRebuildROM();
    }
  };

  const handleAddComponent = (sceneId: string, componentType: ComponentType) => {
    if (componentType === 'palette') {
      const preset = getDefaultPalette(paletteCounter);
      const tempId = `temp-${Date.now()}-${Math.random()}`;

      // Find the next available palette number
      const existingNames = new Set(
        Array.from(scenePalettes.values()).flatMap(map =>
          Array.from(map.values()).map(p => p.name)
        )
      );

      let paletteNumber = 1;
      while (existingNames.has(`Palette ${paletteNumber}`)) {
        paletteNumber++;
      }

      const newPalette: PaletteData = {
        name: `Palette ${paletteNumber}`,
        subPalettes: preset.subPalettes,
        isDirty: true, // New palette, not saved yet
      };

      const currentScenePalettes = scenePalettes.get(sceneId) || new Map();
      currentScenePalettes.set(tempId, newPalette);

      const newScenePalettes = new Map(scenePalettes);
      newScenePalettes.set(sceneId, new Map(currentScenePalettes));
      setScenePalettes(newScenePalettes);

      setPaletteCounter(prev => prev + 1);
    }
  };

  const handlePaletteUpdate = (sceneId: string, paletteId: string, subPalettes: [SubPalette, SubPalette, SubPalette, SubPalette]) => {
    const currentScenePalettes = scenePalettes.get(sceneId);
    if (!currentScenePalettes) return;

    const palette = currentScenePalettes.get(paletteId);
    if (!palette) return;

    const updatedPalette: PaletteData = {
      ...palette,
      subPalettes,
      isDirty: true,
    };

    currentScenePalettes.set(paletteId, updatedPalette);
    const newScenePalettes = new Map(scenePalettes);
    newScenePalettes.set(sceneId, new Map(currentScenePalettes));
    setScenePalettes(newScenePalettes);
  };

  const handlePaletteNameChange = (sceneId: string, paletteId: string, name: string) => {
    const currentScenePalettes = scenePalettes.get(sceneId);
    if (!currentScenePalettes) return;

    const palette = currentScenePalettes.get(paletteId);
    if (!palette) return;

    const updatedPalette: PaletteData = {
      ...palette,
      name,
      isDirty: true,
    };

    currentScenePalettes.set(paletteId, updatedPalette);
    const newScenePalettes = new Map(scenePalettes);
    newScenePalettes.set(sceneId, new Map(currentScenePalettes));
    setScenePalettes(newScenePalettes);
  };

  const handlePaletteSave = async (sceneId: string, paletteId: string) => {
    // DEPRECATED: Components replaced by Assets. This component is not in use.
    // Use AssetDisplay instead for palette management.
    console.warn('ComponentDisplay is deprecated. Use AssetDisplay for palette management.');
  };

  const handleAddEntity = (sceneId: string) => {
    if (!game) return;

    const scene = game.scenes.find(s => s.id === sceneId);
    if (!scene) return;

    const tempId = `temp-${Date.now()}-${Math.random()}`;

    // Find the next available entity number by checking ALL game entities
    // (not just the current scene) to avoid conflicts with the unique constraint
    const existingNames = new Set(
      game.entities?.map(e => e.name) || []
    );

    let entityNumber = 1;
    while (existingNames.has(`Entity ${entityNumber}`)) {
      entityNumber++;
    }

    const newEntity: EntityData = {
      name: `Entity ${entityNumber}`,
      x: 0,
      y: 0,
      isDirty: true, // New entity, not saved yet
    };

    const currentSceneEntities = sceneEntities.get(sceneId) || new Map();
    currentSceneEntities.set(tempId, newEntity);

    const newSceneEntities = new Map(sceneEntities);
    newSceneEntities.set(sceneId, new Map(currentSceneEntities));
    setSceneEntities(newSceneEntities);
  };

  const handleEntityUpdate = (sceneId: string, entityId: string, x: number, y: number) => {
    const currentSceneEntities = sceneEntities.get(sceneId);
    if (!currentSceneEntities) return;

    const entity = currentSceneEntities.get(entityId);
    if (!entity) return;

    const updatedEntity: EntityData = {
      ...entity,
      x,
      y,
      isDirty: true,
    };

    currentSceneEntities.set(entityId, updatedEntity);
    const newSceneEntities = new Map(sceneEntities);
    newSceneEntities.set(sceneId, new Map(currentSceneEntities));
    setSceneEntities(newSceneEntities);
  };

  const handleEntityNameChange = (sceneId: string, entityId: string, name: string) => {
    const currentSceneEntities = sceneEntities.get(sceneId);
    if (!currentSceneEntities) return;

    const entity = currentSceneEntities.get(entityId);
    if (!entity) return;

    const updatedEntity: EntityData = {
      ...entity,
      name,
      isDirty: true,
    };

    currentSceneEntities.set(entityId, updatedEntity);
    const newSceneEntities = new Map(sceneEntities);
    newSceneEntities.set(sceneId, new Map(currentSceneEntities));
    setSceneEntities(newSceneEntities);
  };

  const handleEntitySave = async (sceneId: string, entityId: string) => {
    if (!game) return;

    const currentSceneEntities = sceneEntities.get(sceneId);
    if (!currentSceneEntities) return;

    const entity = currentSceneEntities.get(entityId);
    if (!entity || !entity.isDirty) return;

    const scene = game.scenes.find(s => s.id === sceneId);
    if (!scene) return;

    try {
      const entityData = {
        name: entity.name,
        entity_data: {
          x: entity.x,
          y: entity.y,
        },
      };

      let responseId: string;

      if (entity.id && !entityId.startsWith('temp-')) {
        // Update existing entity
        await EntitiesService.updateEntityGamesGameIdEntitiesEntityIdPut(
          game.id,
          entity.id,
          entityData
        );
        responseId = entity.id;
      } else {
        // Create new entity
        const response = await EntitiesService.createEntityGamesGameIdEntitiesPost(
          game.id,
          entityData
        );
        responseId = response.id;
      }

      // Add entity to scene's entity list if it's not already there
      const currentSceneEntityIds = scene.scene_data.entities || [];
      if (!currentSceneEntityIds.includes(responseId)) {
        const updatedEntityIds = [...currentSceneEntityIds, responseId];

        // Update the scene to include this entity
        await ScenesService.updateSceneGamesGameIdScenesSceneIdPut(
          game.id,
          sceneId,
          {
            scene_data: {
              ...scene.scene_data,
              entities: updatedEntityIds,
            },
          }
        );
      }

      // Update the entity with the real ID from the backend
      const updatedEntity: EntityData = {
        ...entity,
        id: responseId,
        isDirty: false,
      };

      // Replace the temp ID with the real ID if needed
      currentSceneEntities.delete(entityId);
      currentSceneEntities.set(responseId, updatedEntity);

      const newSceneEntities = new Map(sceneEntities);
      newSceneEntities.set(sceneId, new Map(currentSceneEntities));
      setSceneEntities(newSceneEntities);

      // Notify parent to refresh game data
      if (onSceneUpdated) {
        onSceneUpdated();
      }
    } catch (error) {
      console.error('Failed to save entity:', error);
      alert('Failed to save entity');
    }
  };

  if (!game) {
    return (
      <div className={styles.componentDisplayContainer}>
        <div className={styles.componentDisplayHeader}>
          Component Inspector
        </div>
        <div className={styles.componentDisplayContent}>
          <div className={styles.componentDisplayLoading}>
            Loading game data...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.componentDisplayContainer}>
      <div className={styles.componentDisplayHeader}>
        Component Inspector
      </div>

      <div className={styles.componentDisplayContent}>
        <div className={styles.componentDisplayGameHeader}>
          <h3 className={styles.componentDisplayGameTitle}>{game.name}</h3>
          {onRebuildROM && (
            <button
              className={styles.componentDisplayRebuildButton}
              onClick={handleRebuildROMClick}
              title="Save all changes and rebuild ROM"
            >
              <RefreshCw size={16} /> Rebuild ROM
            </button>
          )}
        </div>

        <div className={styles.componentDisplaySection}>
          <h4 className={styles.componentDisplaySectionTitle}>Scenes ({game.scenes.length})</h4>
          {game.scenes.length === 0 ? (
            <p className={styles.componentDisplayEmpty}>No scenes yet</p>
          ) : (
            <ul className={styles.componentDisplayScenesList}>
              {game.scenes.map((scene) => {
                const edit = getSceneEdit(scene.id, scene);
                const currentColorIndex = edit.backgroundColorIndex;
                const currentColor = getNESColor(currentColorIndex);
                const isSaving = saving.has(scene.id);

                // Get list of available palettes from assets
                const availablePalettes = game.assets
                  ?.filter(a => a.type === 'palette') || [];

                return (
                  <li key={scene.id} className={styles.componentDisplaySceneItem}>
                    <div className={styles.sceneItemHeader}>
                      <div className={styles.sceneItemNameRow}>
                        <div className={styles.sceneItemName}>{scene.name}</div>
                        <div className={styles.sceneItemId}>
                          {scene.id.substring(0, 8)}...
                        </div>
                      </div>
                      <button
                        className={`${styles.sceneSaveButton} ${
                          edit.isDirty ? styles.sceneSaveButtonActive : ''
                        }`}
                        onClick={() => handleSaveScene(scene.id)}
                        disabled={!edit.isDirty || isSaving}
                        title={edit.isDirty ? 'Save changes' : 'No changes to save'}
                      >
                        <Save size={16} />
                      </button>
                    </div>

                    <div className={styles.sceneItemContent}>
                      <div className={styles.sceneColorRow}>
                        <span className={styles.sceneColorLabel}>Background:</span>
                        <button
                          className={styles.sceneColorSwatch}
                          style={{ backgroundColor: currentColor }}
                          onClick={(e) => handleColorClick(scene.id, e)}
                          title={`Click to change color (current: ${currentColorIndex})`}
                        />
                        <span className={styles.sceneColorIndex}>
                          ${currentColorIndex.toString(16).toUpperCase().padStart(2, '0')}
                        </span>
                      </div>

                      <div className={styles.sceneColorRow}>
                        <span className={styles.sceneColorLabel}>BG Palette:</span>
                        <select
                          className={styles.scenePaletteSelect}
                          value={edit.backgroundPalette || ''}
                          onChange={(e) => handlePaletteSelect(scene.id, 'background', e.target.value || null)}
                        >
                          <option value="">None</option>
                          {availablePalettes.map(asset => (
                            <option key={asset.id} value={asset.id}>{asset.name}</option>
                          ))}
                        </select>
                      </div>

                      <div className={styles.sceneColorRow}>
                        <span className={styles.sceneColorLabel}>Sprite Palette:</span>
                        <select
                          className={styles.scenePaletteSelect}
                          value={edit.spritePalette || ''}
                          onChange={(e) => handlePaletteSelect(scene.id, 'sprite', e.target.value || null)}
                        >
                          <option value="">None</option>
                          {availablePalettes.map(asset => (
                            <option key={asset.id} value={asset.id}>{asset.name}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Render palettes for this scene */}
                    {scenePalettes.get(scene.id) && (
                      <div className={styles.sceneComponents}>
                        {Array.from(scenePalettes.get(scene.id)!.entries()).map(([paletteId, palette]) => (
                          <PaletteEditor
                            key={paletteId}
                            palette={palette}
                            backgroundColorIndex={currentColorIndex}
                            onUpdate={(colors) => handlePaletteUpdate(scene.id, paletteId, colors)}
                            onNameChange={(name) => handlePaletteNameChange(scene.id, paletteId, name)}
                            onSave={() => handlePaletteSave(scene.id, paletteId)}
                          />
                        ))}
                      </div>
                    )}

                    {/* Component selector */}
                    <ComponentSelector onSelect={(type) => handleAddComponent(scene.id, type)} />

                    {/* Entities section */}
                    <div className={styles.sceneEntitiesSection}>
                      <div className={styles.sceneEntitiesHeader}>
                        <span className={styles.sceneEntitiesTitle}>Entities</span>
                        <button
                          className={styles.addEntityButton}
                          onClick={() => handleAddEntity(scene.id)}
                          title="Add new entity"
                        >
                          <Plus size={14} /> Add Entity
                        </button>
                      </div>
                      {sceneEntities.get(scene.id) && (
                        <div className={styles.sceneEntities}>
                          {Array.from(sceneEntities.get(scene.id)!.entries()).map(([entityId, entity]) => (
                            <EntityEditor
                              key={entityId}
                              entity={entity}
                              onUpdate={(x, y) => handleEntityUpdate(scene.id, entityId, x, y)}
                              onNameChange={(name) => handleEntityNameChange(scene.id, entityId, name)}
                              onSave={() => handleEntitySave(scene.id, entityId)}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        <details className={styles.componentDisplayDetails}>
          <summary className={styles.componentDisplayDetailsSummary}>
            Raw Data
          </summary>
          <pre className={styles.componentDisplayDetailsPre}>
            {JSON.stringify(game, null, 2)}
          </pre>
        </details>
      </div>

      {showColorPicker && (() => {
        const scene = game.scenes.find(s => s.id === showColorPicker);
        if (!scene) return null;
        const edit = getSceneEdit(scene.id, scene);

        return (
          <ColorPicker
            selectedIndex={edit.backgroundColorIndex}
            onSelect={(colorIndex) => handleColorSelect(showColorPicker, colorIndex)}
            onClose={() => {
              setShowColorPicker(null);
              setColorPickerAnchor(null);
            }}
            anchorEl={colorPickerAnchor}
          />
        );
      })()}
    </div>
  );
}

export default ComponentDisplay;
