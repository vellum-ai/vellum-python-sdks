----- GUIDELINES -----

# Conventions

- Modules from the `vellum_ee` directory should _never_ be imported into `src/vellum`
- Every PR to the SDK should accompany with it a new test or an edited test asserting the goal of the PR

## Testing Patterns

- Your PR should avoid editing _unrelated_ tests, unless:
    - You are simplifying the consumer interface and therefore the test itself
    - Your change highlighted an incorrect assumption made by the test
- PR's should strive for max 1 new test or 1 edited test per PR.
- Assertions in the test should be hyper-focused on the goal of the PR and avoid simply copy & pasting assertions from similar tests.
- Fixtures should avoid importing utils from implementation and use their own factories and logic.
