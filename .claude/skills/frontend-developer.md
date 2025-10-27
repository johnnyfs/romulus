# Frontend Developer Skill

This skill provides guidelines and best practices for frontend development in the Romulus project.

## CSS Styling Best Practices

### 1. Use External CSS Files
- **Always** extract inline styles to separate CSS files that match the component filename
  - Component: `Chat.tsx` → CSS file: `Chat.css`
  - Component: `GameDetail.tsx` → CSS file: `GameDetail.css`
- **Never** use inline `style={{}}` props except for truly dynamic values that must be calculated at runtime
- Import CSS files at the top of the component: `import './ComponentName.css'`

### 2. Use CSS Variables
- All common values (colors, sizes, spacing) should be defined in `/src/styles/variables.css`
- Reference variables using `var(--variable-name)`
- **Common variable categories:**
  - Colors: `--color-primary`, `--color-text`, `--bg-white`, etc.
  - Spacing: `--spacing-xs` (4px), `--spacing-sm` (8px), `--spacing-md` (10px), etc.
  - Borders: `--border-color`, `--border-radius-sm`, etc.
  - Typography: `--font-size-sm`, `--font-weight-bold`, etc.

### 3. CSS Class Naming Conventions
- Use BEM-like naming: `block__element--modifier`
- **Examples:**
  - Container: `.chat-container`
  - Child element: `.chat-header`, `.chat-messages`
  - Variants: `.chat-message--user`, `.chat-message--assistant`
- Keep names descriptive and semantic
- Avoid generic names like `.box`, `.container`, `.item`

### 4. CSS Organization
- Group related styles together
- Order: layout → positioning → box model → typography → visual → misc
- Add comments for complex or non-obvious styling

### 5. Responsive Design
- Use CSS Grid and Flexbox for layouts
- Avoid fixed widths where possible
- Use relative units (%, rem, em) over absolute (px) when appropriate
- Consider mobile-first approach

## Component Structure

### Standard Component Pattern
```typescript
import React from 'react';
import './ComponentName.css';

interface ComponentNameProps {
  // Props definition
}

function ComponentName({ prop1, prop2 }: ComponentNameProps) {
  // Component logic

  return (
    <div className="component-container">
      {/* JSX with className instead of style */}
    </div>
  );
}

export default ComponentName;
```

## File Organization

```
frontend/src/
├── components/          # Reusable components
│   ├── Chat.tsx
│   ├── Chat.css
│   ├── RomPlayer.tsx
│   └── RomPlayer.css
├── pages/              # Page-level components
│   ├── GameDetail.tsx
│   ├── GameDetail.css
│   └── CreateGame.tsx
├── styles/             # Global styles
│   ├── variables.css   # CSS variables
│   └── globals.css     # Global styles
└── App.tsx
```

## Code Quality

### TypeScript
- Always define proper interfaces for props
- Use type annotations for complex state
- Avoid `any` type unless absolutely necessary

### React Best Practices
- Use functional components with hooks
- Keep components focused and single-purpose
- Extract reusable logic into custom hooks
- Use proper key props in lists
- Clean up effects and subscriptions

### Performance
- Memoize expensive calculations with `useMemo`
- Memoize callbacks with `useCallback` when passing to child components
- Use `React.memo` for components that render often with same props
- Lazy load routes and heavy components

## Common Patterns

### Form Handling
```typescript
const [value, setValue] = useState('');

const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  // Handle submission
};

const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};
```

### Conditional Rendering
```typescript
// Preferred: Early return for loading/error states
if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;

// For optional content
{isVisible && <OptionalComponent />}

// For either/or
{condition ? <ComponentA /> : <ComponentB />}
```

### CSS Class Composition
```typescript
// Dynamic classes
className={`base-class ${isActive ? 'base-class--active' : ''}`}

// Multiple conditions
className={[
  'base-class',
  isActive && 'base-class--active',
  isDisabled && 'base-class--disabled'
].filter(Boolean).join(' ')}
```

## Future Improvements

- Consider adding a CSS-in-JS solution (styled-components, emotion) for truly dynamic styles
- Implement a design system with reusable UI primitives (Button, Input, Card, etc.)
- Add Storybook for component development and documentation
- Consider adding CSS modules for better style encapsulation
- Implement dark mode support using CSS variables
- Add accessibility (a11y) testing and best practices

## Tools & Libraries

### Currently Used
- React 18
- TypeScript
- React Router
- CSS (vanilla)

### Consider Adding
- **Styling:** styled-components, Tailwind CSS, or CSS Modules
- **UI Components:** Radix UI, shadcn/ui, or Material-UI
- **Forms:** React Hook Form or Formik
- **State Management:** Zustand or Redux Toolkit (if needed)
- **Testing:** Jest, React Testing Library, Playwright
