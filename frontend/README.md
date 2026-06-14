# Harness Builder Frontend

React + Vite frontend for the Harness Builder MVP.

The UI generates and previews an OpenSpec change package, not flat harness
files. After generation, the project detail page shows the package files under
`openspec/changes/setup-ai-harness/`, allows editing/copying, and exports a ZIP.

Use the ZIP by extracting it at the target repository root, then run
`/opsx:apply setup-ai-harness` in that repository.

## Development

```bash
pnpm install
pnpm dev
```

## Tests

```bash
pnpm test
```
