# Technical notes

## Reproduced failure

The reproduced setup used an AMD Radeon RX 9070 XT and a virtual display, with no physical output enabled on the desktop at measurement time.

The game stored 0 MB in `CRenderGPUInfo + 0xb4`, with performance/memory/overall ratings `2/1/1`, and rendered at 960×540. Its monitor cache and Windows/DXGI both reported the currently selected 1920×1080 display mode correctly. The game was in borderless mode.

Independent queries returned 16304 MB through AMD ADL and 16188 MB of dedicated memory through DXGI. ADL display records did not satisfy the game's connected/mapped-display and logical-adapter condition. With a physical output enabled in the earlier measurement, one display did satisfy it.

## Causal path

1. `FUN_141cb4a84` resets the GPU-info memory field to zero.
2. `FUN_141cb4c1c` obtains `DXGI_ADAPTER_DESC` from the current render adapter, then calls `FUN_141cb4ee0` for AMD.
3. That AMD helper only reaches `ADL_Adapter_MemoryInfo_Get` after finding a display with the corresponding logical adapter and `(iDisplayInfoValue & 3) == 3`. Otherwise memory stays zero. The caller does not fall back to the DXGI value in its AMD branch.
4. `FUN_14101c910` accepts a scaled resolution only if estimated MB is strictly less than detected GPU MB. With zero, every candidate fails. `FUN_14194cb5c` renders an empty combo box as `NO DATA`.
5. `FUN_141013440` can force automatic profile 1 when memory is insufficient. `FUN_141012100` maps that profile to 960×540.

The meanings of the ADL connected/mapped flags are documented in the [official AMD ADL header](https://github.com/GPUOpen-LibrariesAndSDKs/display-library/blob/master/include/adl_defines.h).

## Patch

Image base: `0x140000000`. All addresses and offsets below are specific to the accepted file hash.

| Field | Value |
|---|---|
| Changed instruction VA | `0x141cb4cf9` |
| Changed instruction RVA | `0x01cb4cf9` |
| Instruction file offset | `0x01cb42f9` |
| Section | `.arch` |
| Original instruction | `EB 0F`: short jump to `0x141cb4d0a` |
| Patched instruction | `EB E2`: short jump to `0x141cb4cdd` |
| Single changed byte | File offset `0x01cb42fa`, `0F` → `E2` |

This instruction executes immediately after the existing AMD helper call. The original target reads `CRenderGPUInfo + 0xb4`. The new target loads the previously obtained DXGI `DedicatedVideoMemory` value from the caller's stack, converts bytes to MiB, and joins the existing memory-cap/store path.

Conceptually, the AMD branch changes from:

```text
query_amd_gpu_info(info)
memory_MB = info.memory_MB
```

to:

```text
query_amd_gpu_info(info)
memory_MB = render_adapter_desc.DedicatedVideoMemory >> 20
```

Both retain the game's subsequent unsigned minimum with available physical RAM minus 3072 MB. DXGI is used for the AMD branch even when ADL returns a nonzero value; it is a deterministic source associated with the actual render adapter. Other AMD metrics continue to come from the existing helper. This patch does not invent VRAM capacity, force a render resolution, or bypass the resolution memory test.

