# Network lock

ProxyMesh is intentionally locked to the stable hosted **GenLayer Studionet**.

- network alias: `studionet`
- chain ID: `61999`
- GenLayer RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`
- currency: GEN
- required GenLayer CLI: **0.39.1**

Do not migrate this submission to any preview/dev network. The final agent must run `genlayer --version`, `genlayer network set studionet`, and `genlayer network info` before any deployment.

Recommended install if the machine does not already have the exact CLI:

```bash
npm install -g genlayer@0.39.1
```

The CLI may be used only locally on Imani's machine. It is not a project dependency and should not be bundled into the repository.
