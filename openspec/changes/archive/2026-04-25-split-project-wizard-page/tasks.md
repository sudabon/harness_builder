## 1. Frontend Structure

- [x] 1.1 Create a page-specific `frontend/src/pages/project-wizard/` module area for wizard components, constants, and helpers
- [x] 1.2 Move step definitions, initial answers, required fields, checkbox groups, project kinds, and review policies into a constants module without changing values
- [x] 1.3 Add shared wizard prop/type definitions where they reduce duplication between split components

## 2. Frontend Component Split

- [x] 2.1 Extract the left-side wizard progress card into a dedicated component that preserves existing titles, descriptions, and completed/current styling
- [x] 2.2 Extract the preset/project-name step into a dedicated component that preserves custom selection and preset application behavior
- [x] 2.3 Extract the required-items step into a dedicated component that preserves project kind, checkbox group, prohibited actions, and review policy inputs
- [x] 2.4 Extract the optional-items step into a dedicated component that preserves all optional text inputs and textareas
- [x] 2.5 Extract the confirmation step into a dedicated component that preserves selected summary and generated-content summary display
- [x] 2.6 Keep `ProjectWizardPage` as the route-level container responsible for data loading, project creation, answer saving, file generation, navigation, and error/submitting state

## 3. Frontend Behavior Helpers

- [x] 3.1 Extract array-answer toggling into a small helper or stable callback while preserving existing multi-select behavior
- [x] 3.2 Extract current-step validation into a helper and preserve project-name and required-answer validation messages
- [x] 3.3 Preserve the `ensureProject` and `generate` API call order: create project if needed, save answers, generate files, navigate to project detail

## 4. Backend Scope

- [x] 4.1 Confirm no backend API, schema, service, or migration changes are required for this page split

## 5. Verification

- [x] 5.1 Run frontend type checking or build to confirm split imports and props are valid
- [x] 5.2 Run the existing wizard E2E tests to confirm preset reflection, generation, edit save, and ZIP download flows still pass
- [x] 5.3 Add or update focused frontend tests only if the split leaves a behavior gap not covered by existing tests
