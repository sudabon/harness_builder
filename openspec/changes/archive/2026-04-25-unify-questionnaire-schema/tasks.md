## 1. Backend Questionnaire Schema

- [x] 1.1 Add a backend questionnaire schema module that defines answer keys, labels, input types, required flags, allowed options, and defaults
- [x] 1.2 Replace the hard-coded required answer list in project generation with the backend schema definition
- [x] 1.3 Add backend helpers to normalize string and list answer values according to the schema while preserving existing stored JSON format
- [x] 1.4 Update generator context creation to use schema-driven normalization for known answer fields without changing template variable names
- [x] 1.5 Validate backend presets against the schema for known keys, expected value types, and allowed choice values

## 2. Frontend Questionnaire Schema

- [x] 2.1 Add a frontend questionnaire schema module that mirrors backend answer keys, labels, input types, required flags, allowed options, defaults, and wizard step grouping
- [x] 2.2 Replace `project-wizard-page.tsx` hard-coded initial answers with schema-derived initial answers
- [x] 2.3 Replace hard-coded required fields and checkbox/select options with schema-derived values
- [x] 2.4 Preserve existing labels, step flow, preset application behavior, validation message, and answer payload shape
- [x] 2.5 Tighten frontend `AnswerMap` typing where practical without changing the public API client payload shape

## 3. Compatibility Tests

- [x] 3.1 Add backend tests that verify required field detection uses the schema and still reports missing existing required keys
- [x] 3.2 Add backend tests that verify all preset answer keys and choice values are valid according to the schema
- [x] 3.3 Add tests or checks that compare frontend and backend questionnaire schema keys, required flags, and choice values
- [x] 3.4 Preserve existing project answer save/get tests for current `answers` JSON object compatibility
- [x] 3.5 Preserve existing file generation tests to confirm template output remains compatible with current answer keys

## 4. Backend Scope

- [x] 4.1 Confirm no database migration is required because `questionnaire_answers.question_key` and `answer_value` storage remains unchanged
- [x] 4.2 Confirm unknown answer keys are not rejected in a way that breaks existing API clients

## 5. Verification

- [x] 5.1 Run backend tests for projects, presets, and generation
- [x] 5.2 Run frontend type checking or build for the schema-driven wizard changes
- [x] 5.3 Run the existing wizard E2E flow to verify preset reflection, answer entry, generation, and project-detail navigation still work
