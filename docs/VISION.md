# NordOS vision

The [design bible](DESIGN_BIBLE.md) and [project README](../README.md) are the current consolidated direction. This page retains earlier implementation sketches; setup, assistant surfaces, desktop alternatives, and replacement mechanisms remain proposals. Current upstream Cutefish work takes priority.

NordOS is an operating-system project with an attractive default desktop and an integrated conversational assistant. The desktop should work comfortably on its own, while the assistant provides a fast way to find things, control applications, understand the system, and make changes.

## First-run setup

A proposed first-run experience offers conversational help with choosing a starting environment and software. Ordinary graphical setup must remain complete without requiring AI engagement.

- Recommend the NordOS default desktop and a useful default application set.
- Ask what the person wants to do with the computer and tailor the software selection to those needs.
- Offer alternatives, including GNOME and KDE Plasma, for people who prefer them.
- Show the selected desktop and applications before applying the setup.
- Let people revisit these choices later.

The recommended desktop provides the most integrated starting experience. Alternative desktop environments are part of the intended product direction; their installation and integration still need implementation and testing.

## Everyday use: a super-powered Spotlight

NordOS is AI native without forcing AI engagement. Ordinary search should find and launch applications directly. Questions should receive context-aware answers, with clarification when necessary. Relevant current system state should inform reliable and safe changes through managed system interfaces.

After setup, the normal starting point is the selected desktop. A system-wide shortcut opens a compact assistant that combines search, launching, commands, and conversation.

For a short request, the assistant should be quick to open, act, and dismiss. For longer work, it can expand into a chat window or panel with task history, progress, and useful context.

Examples of intended interactions include:

- Find a file, launch an application, or move between windows.
- Install software suited to a task.
- Change settings or explain the current configuration.
- Diagnose a hardware or service problem.
- Work inside installed applications.
- Design a custom interface or create a new application.

Graphical applications, ordinary desktop controls, and the assistant remain available together. The assistant is intended to be useful across the supported desktop choices, with desktop-specific adapters where their integration interfaces differ.

## Capabilities, starting with the working tools

The first version builds on the current screenshot, keyboard, mouse, application, and window-control capabilities demonstrated by Cutefish's computer-use interface.

The next layer adds direct, structured access to system information so the assistant can inspect relevant facts without repeatedly reading them from the screen. Candidate read-only tools include:

- OS, kernel, installed software, package versions, and available updates.
- CPU, GPU, memory, disks, audio devices, drivers, firmware, and device capabilities.
- Service state, device state, diagnostic logs, and resource usage.
- Audio routing, mute and volume state, displays, sessions, and desktop configuration.

System changes should use suitable native tools or service interfaces where available. Screen interaction remains a way to work with applications and interfaces that need it.

For example, an audio diagnosis could read the detected controller, codec, driver, active output, and mixer settings before deciding which change to propose. Hardware-specific workarounds should be scoped to the matching hardware.

## Initial architecture to explore

- **Setup experience:** conversational first-run choices for desktop and software.
- **Integrated assistant:** compact launcher/search surface with an expandable chat and task view.
- **Agent runtime:** interprets requests and coordinates tools, applications, and ongoing work.
- **System-state tools:** return structured hardware, package, service, and diagnostic information.
- **System-action tools:** perform supported changes through native interfaces and report the result.
- **Desktop adapters:** integrate the assistant and application control with the selected desktop.
- **Desktop and distribution foundation:** display/input/window handling, sessions, packages, images, installation, updates, and recovery.

Read-only inspection and operations that change the system should be distinguishable. Routine work uses ordinary user access; privileged operations go through explicit system interfaces. Users should be able to see what changed, interrupt work, and recover from a failed operation.

## Gradual replacement

Cutefish supplies an initial working foundation and implementation knowledge. NordOS will progressively replace inherited pieces with its own native components.

1. Preserve a working baseline and its upstream history.
2. Learn each component's responsibilities and interfaces.
3. Replace one component at a time with a NordOS implementation.
4. Check compatibility and daily usability before replacing the next piece.

The implementation languages, model providers, and long-term distribution base remain open design decisions.

## First milestones

- Establish the component forks and their source/license inventory.
- Reproduce the upstream desktop in a development VM using the existing Debian 13 build path.
- Prototype the integrated assistant as a normal application with a global entry point in that desktop.
- Connect the existing screenshot and input controls.
- Add structured system-state and hardware queries, followed by a small set of system actions.
- Prototype conversational first-run desktop and software selection.
- Add and test GNOME/KDE integration alongside the recommended default desktop.
- Replace inherited components incrementally as the NordOS interfaces become clear.

This repository records the project direction and source foundation. The setup experience, integrated assistant, native tools, alternative-desktop integration, and NordOS image remain planned work.
