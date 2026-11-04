# Development and build baseline

The first milestone is to reproduce a working Cutefish desktop in a development VM, then prototype the integrated NordOS assistant inside it.

The upstream project currently develops and tests against Debian 13. Its complete build instructions, dependency list, component ordering, and session setup are in [cutefishos/getting-started](https://github.com/cutefishos/getting-started). The package and live-image build path is in [cutefishos/packaging](https://github.com/cutefishos/packaging).

## Source layout

Keep component checkouts side by side under their original component directory names. The renamed NordOS repository fills the `cutefish-core` position:

```text
development/
  cutefish-toolkit/
  cutefish-framework/
  cutefish-core/          # clone of serjykalstryke/NordOS
  cutefish-compositor/
  filemanager/
  settings/
  terminal/
  packaging/
  ...
```

Use the verified fork URLs in `components.json`. Entries still awaiting a fork contain an upstream URL and a pinned starting commit so their original source remains available.

For the core checkout:

```sh
git clone https://github.com/serjykalstryke/NordOS.git cutefish-core
git -C cutefish-core remote add upstream https://github.com/cutefishos/cutefish-core.git
```

## Build order and runtime

Follow the upstream build guide for the exact dependency order and commands. The toolkit and its pinned Skia sources come first, followed by the framework and the components that depend on them. The current source build uses `/usr` as its install prefix. The computer-use component uses Cargo; the other application and desktop components use CMake.

Start with the ordinary Cutefish session in a VM as the recommended desktop baseline. Add the integrated assistant as an application with a global entry point and an expandable chat window. The selected desktop remains the everyday workspace.

Develop conversational first-run desktop/software selection separately from normal desktop use. GNOME and KDE Plasma are intended alternatives; their package selection, session setup, assistant entry point, and application-control integration need their own validation. Keep the assistant's system-state tools separate from desktop-specific adapters so they can be shared across these environments.

## Distribution tooling

The packaging repository contains Debian package definitions and a Debian live-build ISO configuration. Its existing image configuration consumes upstream Cutefish packages. NordOS package sources, branding, signing, update channels, and image publication still need design and implementation before a NordOS image can be produced.

The installer repository contains privileged disk-installation code. It belongs to the eventual live-image pipeline; this setup does not run it or change the current laptop's installation.

## Validation status

This repository setup preserves the existing source and records its starting commits. A fresh desktop build, NordOS image build, and conversational-shell implementation have not been performed as part of the fork setup.
