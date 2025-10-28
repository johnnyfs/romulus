import { useState } from 'react';
import { Save } from 'lucide-react';
import styles from './EntityEditor.module.css';

export interface EntityData {
  id?: string;
  name: string;
  x: number;
  y: number;
  isDirty: boolean;
}

interface EntityEditorProps {
  entity: EntityData;
  onUpdate: (x: number, y: number) => void;
  onNameChange: (name: string) => void;
  onSave: () => void;
}

function EntityEditor({ entity, onUpdate, onNameChange, onSave }: EntityEditorProps) {
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
    </div>
  );
}

export default EntityEditor;
