# E2E Workdirs

This directory contains cloned project fixtures for end-to-end scenario tests. Each fixture is a full checkout of a real open-source project at a pinned commit.

## How to set up a fixture

1. Clone the project:
   ```
   git clone <repo-url> <workdir-name>
   ```

2. Checkout the pinned commit:
   ```
   cd <workdir-name>
   git checkout <commit-hash>
   ```

3. Verify:
   ```
   git log -1 --oneline
   ```

## Fixture requirements

- Clone depth: `--depth 1` is acceptable for smaller repos. Use full clones for repos where `--depth 1` omits needed history.
- The pinned commit must be publicly accessible from the upstream repo.
- Do not modify fixture files — tests expect pristine upstream source.

## Current fixtures

| Directory | Upstream Repo | Commit | Scenario |
|-----------|--------------|--------|----------|
| `003-add-avatar-upload/` | `github.com/go-admin-team/go-admin` | (pinned) | 003-add-avatar-upload |

## Notes

- Fixture directories are excluded from git via `../.gitignore`.
- Only scenario JSON files and this README are tracked in git.
- To add a new fixture, clone it here, then update this README and the corresponding scenario JSON.
