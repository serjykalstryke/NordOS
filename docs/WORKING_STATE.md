# NordOS working state

This checkpoint contains the NordOS foundation and Typewriter 0.2, a lightweight writing profile for 64-bit UEFI systems. It records the tested foundation based on `80bffb1` and the Typewriter build that reused its power interface. The checkpoint is on the `working-state` branch for continued development.

## Foundation

The core is organized into the System Library, System Services, Desktop, and Linux Platform layers. Session composition selects the desktop processes at build time. The development VM recipe stages the foundation on Debian and starts its Wayland desktop.

- [System architecture](SYSTEM_ARCHITECTURE.md)
- [Foundation implementation and validation](FOUNDATION_STATUS.md)
- [Development VM build and boot](../distribution/image/README.md)

## Typewriter

The [Typewriter source](../distribution/typewriter/) contains the offline installer, its BYOK Studio and Obsidian app records, the session launcher, and the Nord-inspired Plymouth theme. The desktop installer uses System Library calls. Installation policy lives in System Services, with separate Debian package, Linux execution, disk, boot, and power implementations. The installer saves one app as the startup app.

The USB preview and offline installation were exercised for both apps in UEFI virtual machines. Each installation booted from its own disk into the selected app. The final installer’s **Shut Down** button also passed. Physical MacBook testing is pending.

The personal test ISO is available separately. The public source records the expected package versions and hashes, with downloads obtained directly from the app publishers. [Typewriter build guide](../distribution/typewriter/README.md)
