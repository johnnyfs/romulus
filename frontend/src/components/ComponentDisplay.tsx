import { useState, useEffect } from 'react';
import { Save, RefreshCw } from 'lucide-react';
import styles from './ComponentDisplay.module.css';
import type { GameGetResponse } from '../client/models/GameGetResponse';
import { ScenesService } from '../client/services/ScenesService';
import { ComponentsService } from '../client/services/ComponentsService';
import { getNESColor } from '../constants/nesColors';
import { getDefaultPalette } from '../constants/palettePresets';
import ColorPicker from './ColorPicker';
import PaletteEditor, { type PaletteData, type SubPalette } from './PaletteEditor';
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

  // Initialize scenePalettes from game.components when game loads
  useEffect(() => {
    if (!game || !game.components) return;

    const newScenePalettes = new Map<string, Map<string, PaletteData>>();

    // For each scene, find all palette components
    game.scenes.forEach(scene => {
      const scenePaletteMap = new Map<string, PaletteData>();

      // Add all palette components to this scene
      // Note: Currently components are global, so we show them on all scenes
      // You might want to filter by scene-specific components later
      game.components.forEach(component => {
        if (component.component_data.type === 'palette' && component.component_data.palettes) {
          const paletteData: PaletteData = {
            id: component.id,
            name: component.name,
            subPalettes: component.component_data.palettes.map(palette =>
              palette.colors.map(color => color.index) as SubPalette
            ) as [SubPalette, SubPalette, SubPalette, SubPalette],
            isDirty: false,
          };
          scenePaletteMap.set(component.id, paletteData);
        }
      });

      if (scenePaletteMap.size > 0) {
        newScenePalettes.set(scene.id, scenePaletteMap);
      }
    });

    setScenePalettes(newScenePalettes);
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
    if (!game) return;

    const currentScenePalettes = scenePalettes.get(sceneId);
    if (!currentScenePalettes) return;

    const palette = currentScenePalettes.get(paletteId);
    if (!palette || !palette.isDirty) return;

    try {
      const componentData = {
        name: palette.name,
        component_data: {
          type: 'palette',
          palettes: palette.subPalettes.map(subPalette => ({
            colors: subPalette.map(index => ({ index })),
          })),
        },
      };

      let responseId: string;

      if (palette.id && !paletteId.startsWith('temp-')) {
        // Update existing palette
        await ComponentsService.updateComponentGamesGameIdComponentsComponentIdPut(
          game.id,
          palette.id,
          componentData
        );
        responseId = palette.id;
      } else {
        // Create new palette
        const response = await ComponentsService.createComponentGamesGameIdComponentsPost(
          game.id,
          componentData
        );
        responseId = response.id;
      }

      // Update the palette with the real ID from the backend
      const updatedPalette: PaletteData = {
        ...palette,
        id: responseId,
        isDirty: false,
      };

      // Replace the temp ID with the real ID if needed
      currentScenePalettes.delete(paletteId);
      currentScenePalettes.set(responseId, updatedPalette);

      const newScenePalettes = new Map(scenePalettes);
      newScenePalettes.set(sceneId, new Map(currentScenePalettes));
      setScenePalettes(newScenePalettes);

      // Notify parent to refresh game data
      if (onSceneUpdated) {
        onSceneUpdated();
      }
    } catch (error) {
      console.error('Failed to save palette:', error);
      alert('Failed to save palette');
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

                // Get list of available palettes from components
                const availablePalettes = game.components
                  ?.filter(c => c.component_data.type === 'palette')
                  .map(c => c.name) || [];

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
                          {availablePalettes.map(name => (
                            <option key={name} value={name}>{name}</option>
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
                          {availablePalettes.map(name => (
                            <option key={name} value={name}>{name}</option>
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
