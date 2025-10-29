import { useState } from 'react';
import { Save, Plus, X } from 'lucide-react';
import styles from './EntityEditor.module.css';
import type { NESSpriteData } from '../client/models/NESSpriteData';
import type { NESPaletteData_Output } from '../client/models/NESPaletteData_Output';

type ComponentData = NESSpriteData | NESPaletteData_Output;

export interface EntityData {
  id?: string;
  name: string;
  x: number;
  y: number;
  components?: ComponentData[];
  isDirty: boolean;
}

interface EntityEditorProps {
  entity: EntityData;
  onUpdate: (x: number, y: number) => void;
  onNameChange: (name: string) => void;
  onComponentsChange: (components: ComponentData[]) => void;
  onSave: () => void;
  spriteSize: '8x8' | '8x16';  // Game's sprite size setting
}

function EntityEditor({ entity, onUpdate, onNameChange, onComponentsChange, onSave, spriteSize }: EntityEditorProps) {
  const [xInput, setXInput] = useState(entity.x.toString());
  const [yInput, setYInput] = useState(entity.y.toString());

  const handleXChange = (value: string) => {
    setXInput(value);
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 255) {
      onUpdate(numValue, entity.y);
    }
  };

  const handleYChange = (value: string) => {
    setYInput(value);
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 255) {
      onUpdate(entity.x, numValue);
    }
  };

  const handleAddSprite = () => {
    const components = entity.components || [];
    const hasSprite = components.some(c => c.type === 'sprite');

    if (hasSprite) {
      alert('Entity already has a sprite component');
      return;
    }

    const newSprite: NESSpriteData = {
      type: 'sprite',
      width: 1,
      height: 1,
      sprite_set: null,
    };

    onComponentsChange([...components, newSprite]);
  };

  const handleSpriteChange = (index: number, width: number, height: number) => {
    const components = entity.components || [];
    const updated = [...components];
    updated[index] = {
      ...updated[index],
      width,
      height,
    } as NESSpriteData;
    onComponentsChange(updated);
  };

  const handleRemoveComponent = (index: number) => {
    const components = entity.components || [];
    onComponentsChange(components.filter((_, i) => i !== index));
  };

  const getPixelDimensions = (width: number, height: number) => {
    if (spriteSize === '8x8') {
      return { w: width * 8, h: height * 8 };
    } else {
      return { w: width * 8, h: height * 16 };
    }
  };

  return (
    <div className={styles.entityEditor}>
      <div className={styles.entityHeader}>
        <input
          type="text"
          className={styles.entityName}
          value={entity.name}
          onChange={(e) => onNameChange(e.target.value)}
        />
        <button
          className={`${styles.entitySaveButton} ${entity.isDirty ? styles.entitySaveButtonActive : ''}`}
          onClick={onSave}
          disabled={!entity.isDirty}
          title={entity.isDirty ? 'Save entity' : 'No changes to save'}
        >
          <Save size={14} />
        </button>
      </div>
      <div className={styles.entityFields}>
        <div className={styles.entityField}>
          <label className={styles.entityLabel}>X:</label>
          <input
            type="number"
            className={styles.entityInput}
            value={xInput}
            onChange={(e) => handleXChange(e.target.value)}
            min="0"
            max="255"
          />
        </div>
        <div className={styles.entityField}>
          <label className={styles.entityLabel}>Y:</label>
          <input
            type="number"
            className={styles.entityInput}
            value={yInput}
            onChange={(e) => handleYChange(e.target.value)}
            min="0"
            max="255"
          />
        </div>
      </div>

      {/* Components section */}
      <div className={styles.componentsSection}>
        <div className={styles.componentsHeader}>
          <span className={styles.componentsTitle}>Components</span>
          <button
            className={styles.addComponentButton}
            onClick={handleAddSprite}
            title="Add sprite component"
          >
            <Plus size={12} /> Sprite
          </button>
        </div>

        {entity.components && entity.components.length > 0 && (
          <div className={styles.componentsList}>
            {entity.components.map((component, index) => {
              if (component.type === 'sprite') {
                const sprite = component as NESSpriteData;
                const pixels = getPixelDimensions(sprite.width, sprite.height);
                return (
                  <div key={index} className={styles.componentItem}>
                    <div className={styles.componentHeader}>
                      <span className={styles.componentType}>Sprite</span>
                      <button
                        className={styles.removeComponentButton}
                        onClick={() => handleRemoveComponent(index)}
                        title="Remove component"
                      >
                        <X size={12} />
                      </button>
                    </div>
                    <div className={styles.componentContent}>
                      <div
                        className={styles.spritePreview}
                        style={{
                          width: `${pixels.w * 2}px`,
                          height: `${pixels.h * 2}px`,
                        }}
                        title={`${pixels.w}x${pixels.h} pixels`}
                      />
                      <div className={styles.componentFields}>
                        <div className={styles.componentField}>
                          <label>Width:</label>
                          <input
                            type="number"
                            value={sprite.width}
                            onChange={(e) => handleSpriteChange(index, parseInt(e.target.value) || 1, sprite.height)}
                            min="1"
                            max="16"
                          />
                          <span className={styles.pixelSize}>({pixels.w}px)</span>
                        </div>
                        <div className={styles.componentField}>
                          <label>Height:</label>
                          <input
                            type="number"
                            value={sprite.height}
                            onChange={(e) => handleSpriteChange(index, sprite.width, parseInt(e.target.value) || 1)}
                            min="1"
                            max="16"
                          />
                          <span className={styles.pixelSize}>({pixels.h}px)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default EntityEditor;
