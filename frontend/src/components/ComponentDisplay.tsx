import { useState } from 'react';
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
  isDirty: boolean;
}

interface ScenePalettes {
  sceneId: string;
  palettes: Map<string, PaletteData>; // temp ID -> PaletteData
}

function ComponentDisplay({ game, onRebuildROM, onSceneUpdated }: ComponentDisplayProps) {
  const [editingScenes, setEditingScenes] = useState<Map<string, SceneEdit>>(new Map());
  const [showColorPicker, setShowColorPicker] = useState<string | null>(null);
  const [colorPickerAnchor, setColorPickerAnchor] = useState<HTMLElement | null>(null);
  const [saving, setSaving] = useState<Set<string>>(new Set());
  const [scenePalettes, setScenePalettes] = useState<Map<string, Map<string, PaletteData>>>(new Map());
  const [paletteCounter, setPaletteCounter] = useState(0);

  const getSceneEdit = (sceneId: string, originalColorIndex: number): SceneEdit => {
    return editingScenes.get(sceneId) || {
      sceneId,
      backgroundColorIndex: originalColorIndex,
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

    const originalColorIndex = scene.scene_data.background_color.index;
    const newEditingScenes = new Map(editingScenes);
    newEditingScenes.set(sceneId, {
      sceneId,
      backgroundColorIndex: colorIndex,
      isDirty: colorIndex !== originalColorIndex,
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

      const newPalette: PaletteData = {
        name: preset.name,
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

  const handlePaletteSave = async (sceneId: string, paletteId: string) => {
    if (!game) return;

    const currentScenePalettes = scenePalettes.get(sceneId);
    if (!currentScenePalettes) return;

    const palette = currentScenePalettes.get(paletteId);
    if (!palette || !palette.isDirty) return;

    try {
      // Create the component on the backend with all 4 sub-palettes
      const response = await ComponentsService.createComponentGamesGameIdComponentsPost(
        game.id,
        {
          name: palette.name,
          component_data: {
            type: 'palette',
            palettes: palette.subPalettes.map(subPalette => ({
              colors: subPalette.map(index => ({ index })),
            })),
          },
        }
      );

      // Update the palette with the real ID from the backend
      const updatedPalette: PaletteData = {
        ...palette,
        id: response.id,
        isDirty: false,
      };

      // Replace the temp ID with the real ID
      currentScenePalettes.delete(paletteId);
      currentScenePalettes.set(response.id, updatedPalette);

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
                const edit = getSceneEdit(scene.id, scene.scene_data.background_color.index);
                const currentColorIndex = edit.backgroundColorIndex;
                const currentColor = getNESColor(currentColorIndex);
                const isSaving = saving.has(scene.id);

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
        const edit = getSceneEdit(scene.id, scene.scene_data.background_color.index);

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
