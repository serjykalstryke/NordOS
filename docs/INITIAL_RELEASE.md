# Initial NordOS release plan

Status: proposed implementation sequence, November 10, 2026. Repository acquisition is underway; this is not a completed NordOS image or a completed build.

## Source acquisition

Nineteen of the original twenty-two repositories are verified GitHub forks under serjykalstryke, with their expected cutefishos parent. Ten forks were added in this attempt: packaging, getting-started, cutefish-installer, icons, text-editor, qt-plugins, calculator, video-player, plymouth-theme, and cutefish-computer-use.

Wallpapers, system-monitor, and calendar remain pending. GitHub repeatedly returned “was submitted too quickly” during creation. Their pinned upstream commits in components.json remain usable for development. Keep the November 4 baseline pins unchanged; fork creation does not automatically select newer code as a tested baseline.

The current packaging versions file also includes cutefish-webkit 2.54.2. Audit its consumers, source pin, dependencies, build time, license notices, and whether the first image needs it before extending the original inventory. The packaging-local cutefish-desktop metapackage is not a separate upstream repository.

## First deliverable

Produce a reproducible NordOS development image that boots into a usable graphical desktop, identifies itself as NordOS, installs the chosen application set, and preserves ordinary graphical operation without AI. Integrate AI incrementally through the design bible's intent and system-awareness principles. An initial image need not implement kernel replaceability or universal compatibility.

## Keep the working foundation

Retain the toolkit, framework, session services, compositor, file manager, settings, icon theme, and essential integration until replacements have passed equivalent checks. File Manager also draws the desktop; the compositor contains shell, dock, launcher, and lock-screen responsibilities. These are coupled components, so removal requires identifying and replacing their responsibilities first.

Keep upstream remotes, history, license files, attribution, protocol identifiers, and package names until a specific change requires otherwise. Product branding can change before internal API and package names. Avoid a global Cutefish-to-NordOS replacement that breaks executable paths, desktop entries, service names, or dependent packages.

## Separate the product composition

Introduce a NordOS package profile rather than treating the inherited cutefish-desktop metapackage as the final product definition. That metapackage currently depends on a complete application set and cutefish-dm. Decide explicitly which applications are defaults, which are optional, and which display manager belongs in the image. Keep existing host login and desktop settings untouched during development.

Define independently reviewable changes for branding and session entries; default applications and dock entries; shell layout and search; setup; application services; and AI integration. Remove obsolete UI only when its replacement is available or its capability is intentionally excluded from the product profile.

## Make the build consume NordOS sources

The packaging build workflow currently fetches cutefishos repositories, and the ISO consumes packages from download.cutefish.org. A fork alone changes neither behavior.

Add an explicit source mapping so the core component resolves to serjykalstryke/NordOS while retaining the cutefish-core checkout directory. Resolve other components to their forks, with documented pinned upstream fallback for pending forks. Select a tested commit set, including the existing toolkit Snap integration where required, rather than silently using every repository's latest HEAD.

Build Debian packages from those sources in an isolated Debian 13 environment. Define a NordOS package version policy, repository, signing process, and update channel. Point image builds at the resulting package set and record the exact source and package manifest. Do not enable inherited publishing workflows until their destinations and credentials have been reviewed for NordOS.

## Validation gates

1. Reproduce the baseline desktop and retain build logs and source pins.
2. Build the NordOS package composition and install it in a disposable VM.
3. Verify boot, login, logout, lock and unlock, file operations, network, audio, settings, launch, install, update, and removal.
4. Verify graphical search and application launch without conversational interruption, including when AI is unavailable.
5. Test AI inspection and a small set of managed actions against current state, with clear failure and recovery behavior.
6. Build a bootable image from the verified packages; test live boot and installation onto a disposable virtual disk.
7. Record known limitations and repeat the same checks after each component removal or replacement.

The next engineering milestone is the source-mapped package build and a reproducible VM baseline. No desktop components have been stripped out, no display manager has been changed, and no ISO build has been performed in this acquisition task.
