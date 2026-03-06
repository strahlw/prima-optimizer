# 🚀 Git / Release Workflow Strategy

## 📁 Branch Roles

-   `main`

    -   Production-ready code only.
    -   Always deployable.

-   `release/x.y.z-rc.#`

    -   Features in UAT.
    -   Used to prepare, test, and validate a release.

-   `develop`

    -   Features ready for QA.
    -   Next batch of features that are candidates for a release.

-   `next`

    -   Cutting-edge development.
    -   Features in progress, not yet QA-ready.

---

## 🔁 Back-porting Fixes from Release to Develop and Next

When changes are made on a `release/*` branch (e.g., from UAT feedback), those changes should be cherry-picked into both `develop` and `next` to keep all branches up to date.

### ✅ Steps:

```bash
# On the release branch
git checkout release/0.3.1-rc.2
git log --oneline
# Find the commit hash (e.g. abc123)

# Cherry-pick into develop
git checkout develop
git cherry-pick abc123
git push origin develop

# Cherry-pick into next
git fetch origin next
git merge develop # Ensure next has latest from develop
git push origin next
```

---

## 🧼 Best Practices

-   Use **Conventional Commits**.
-   Use **squash merges** for feature branches to keep history clean.
-   **Do not squash** when merging `release/*` into `main` — preserve release history.
-   Always **tag** pre-releases (`vX.Y.Z-rc.N`) and final releases (`vX.Y.Z`).
-   Prefer **cherry-pick** over merge to avoid bringing unstable changes into `develop` and `next`.
-   Handle conflicts during cherry-picks using:
    ```bash
    git status
    # resolve conflicts
    git add .
    git cherry-pick --continue
    ```

---

## 📚 Summary Diagram

```
          feature/* → next ┐
                          ├──> develop ──────┐
UAT fixes → release/0.3.1 ┘                 ↓
       ↑          ↓                        ↓
      main ←──────┴─────────────── v0.3.1 (final)
```
