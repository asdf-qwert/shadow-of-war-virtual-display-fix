# Shadow of War virtual display fix

A reversible one-byte patch for the Windows x64 build of **Middle-earth: Shadow of War**. One Python tool supports Windows and Linux installations using Proton/Wine. Python 3.8 or newer is required; there are no third-party dependencies.

When using a virtual display with an AMD GPU, the game may incorrectly detect **0 MB VRAM**. This can leave the scaled-resolution menu empty, displaying **NO DATA**, and cause automatic settings to select **960x540**.

The AMD ADL memory query is incorrectly gated on finding a connected, mapped display. This patch keeps the AMD information query, then obtains dedicated memory from the render adapter's existing DXGI description. The game's memory cap and resolution filtering remain in place. NVIDIA and Intel branches are unchanged.

## Usage

Download `patch.py`, close the game, and run with Python 3 available as `python`:

```sh
python patch.py "PATH/TO/ShadowOfWar/x64/ShadowOfWar.exe"
```

Replace the path with your game installation. The script verifies the EXE hash, saves an original backup, changes one byte, and verifies the result. Re-running it leaves an already patched file unchanged.

To undo: close the game, remove the patched EXE, and rename `ShadowOfWar.exe.sow-vram-fix.original` to `ShadowOfWar.exe`.

Supports the exact Steam build **1.0.8874.0** identified by the hashes in `patch.py`. Other builds are refused.

## Disclaimer

Use at your own risk. This patch is provided without warranty; see [LICENSE](LICENSE).

This is an unofficial community project, not affiliated with or endorsed by the game's developers, publishers, or rights holders. Game-related trademarks and copyrights belong to their respective owners. No game binaries or assets are distributed. The MIT license applies only to this project's original code and documentation.

[Technical details](docs/technical.md) · [MIT license](LICENSE)
