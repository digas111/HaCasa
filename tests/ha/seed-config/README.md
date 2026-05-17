# Home Assistant Seed Config

Files in this directory are copied into `.ha-test/config` by `scripts/ha-test/prepare.js`.

Only store safe, reproducible Home Assistant state here. Do not commit auth files,
tokens, UUIDs, recorder databases, logs, or runtime locks.

To refresh this seed from a configured local `.ha-test/config`, run:

```sh
npm run test:ha:snapshot-seed
```

For a full machine-local backup, use `npm run test:ha:snapshot-local`. Those
archives are written to `.ha-test-backups/` and are intentionally git-ignored.
