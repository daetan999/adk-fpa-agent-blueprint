```markdown
# adk-fpa-agent-blueprint Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `adk-fpa-agent-blueprint` TypeScript codebase. You'll learn how to structure files, write imports/exports, follow commit message guidelines, and write tests. This guide ensures consistency and maintainability for contributors.

## Coding Conventions

### File Naming
- **Style:** kebab-case
- **Example:**  
  ```
  user-profile.ts
  agent-handler.test.ts
  ```

### Import Style
- **Style:** Relative imports
- **Example:**
  ```typescript
  import { AgentHandler } from './agent-handler';
  import { UserProfile } from '../models/user-profile';
  ```

### Export Style
- **Style:** Named exports
- **Example:**
  ```typescript
  // agent-handler.ts
  export function handleAgent() { ... }

  // Usage
  import { handleAgent } from './agent-handler';
  ```

### Commit Messages
- **Pattern:** Conventional commits
- **Prefix Example:** `docs: update README with usage instructions`
- **Average Length:** ~43 characters

  **Example:**
  ```
  docs: add API usage examples to documentation
  ```

## Workflows

### Making Documentation Updates
**Trigger:** When updating or adding documentation files.
**Command:** `/docs-update`

1. Edit or add documentation in the appropriate files (e.g., `README.md`).
2. Use a conventional commit message with the `docs:` prefix.
   ```
   docs: update installation instructions
   ```
3. Push your changes and open a pull request if required.

## Testing Patterns

- **Framework:** Unknown (no explicit framework detected)
- **File Naming:** Test files follow the `*.test.*` pattern.
  - **Example:** `agent-handler.test.ts`
- **Typical Structure:**
  ```typescript
  import { handleAgent } from './agent-handler';

  describe('handleAgent', () => {
    it('should process agent correctly', () => {
      // test implementation
    });
  });
  ```

## Commands
| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /docs-update   | Update or add documentation files            |
```
