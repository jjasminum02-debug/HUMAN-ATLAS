# T22 test-only motion fixtures

These fixtures derive from the isolated synthetic T20 contract fixture and add one explicitly synthetic combined representation. IDs, asset bytes, node names, and values are test-only; no fixture is imported by learner content or `atlas-data/assets`. The positive case binds moving bone IDs through `rig.nodeBindings` and action muscle/part subject IDs through `illustration.trajectoryBindings`. The negative case is produced in memory by the T22 validator test.
