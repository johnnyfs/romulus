import { useState, useRef, useEffect } from 'react';
import { Plus } from 'lucide-react';
import styles from './ComponentSelector.module.css';

export type ComponentType = 'palette';

interface ComponentSelectorProps {
  onSelect: (type: ComponentType) => void;
}

function ComponentSelector({ onSelect }: ComponentSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleSelect = (type: ComponentType) => {
    onSelect(type);
    setIsOpen(false);
  };

  return (
    <div className={styles.componentSelectorContainer} ref={dropdownRef}>
      <button
        className={styles.componentSelectorButton}
        onClick={() => setIsOpen(!isOpen)}
        title="Add component"
      >
        <Plus size={16} /> Add Component
      </button>

      {isOpen && (
        <div className={styles.componentSelectorDropdown}>
          <button
            className={styles.componentSelectorOption}
            onClick={() => handleSelect('palette')}
          >
            Palette
          </button>
        </div>
      )}
    </div>
  );
}

export default ComponentSelector;
