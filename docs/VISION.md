# NordOS vision

NordOS is an operating-system project built around a polished conversational workspace. The starting screen should feel as direct as a terminal and as approachable as a chat, with a visual interface people want to use every day.

The user describes an outcome, and the computer helps carry it out: opening and controlling applications, installing software, changing settings, designing interfaces, and creating new software. The conversation remains available as the workspace evolves.

## A workspace that can grow

The conversational shell is the intended default. People can also install a traditional desktop environment, use ordinary applications, or design a custom interface using the Cutefish components as a starting point. Existing graphical tools remain useful alongside conversation.

Interfaces should appear when they help the task: an editor for code, a form for structured input, a panel for a running operation, a file browser for organizing documents, or a custom application built for the user's workflow.

## Gradual replacement

Cutefish provides an initial working foundation and a source of implementation knowledge. NordOS will progressively replace inherited pieces with its own native components.

The guiding approach is to keep a usable system throughout that transition:

1. Preserve a working baseline and its upstream history.
2. Learn each component's responsibilities and interfaces.
3. Replace one component at a time with a NordOS implementation.
4. Check compatibility and daily usability before replacing the next piece.

The architecture, implementation language, model providers, and long-term distribution base remain open design decisions.

## Initial layers to explore

- **Conversational shell:** the default workspace, conversation history, command entry, and task views.
- **Agent runtime:** translates requests into inspectable actions and coordinates tools and applications.
- **System integration:** package management, files, settings, services, application launch, and desktop control.
- **Interface composition:** opens existing applications and assembles new panels or applications around a task.
- **Desktop foundation:** display, input, windows, portals, login/session management, and accessibility.
- **Distribution tooling:** reproducible packages, images, installation, updates, and recovery.

The agent should use ordinary user access for routine work and request privileged system operations through explicit system interfaces. A user should be able to see what changed, interrupt work, and recover from a failed change.

## First milestones

- Establish the component forks and an inventory of their origins and licenses.
- Reproduce the upstream desktop in a development VM using the existing Debian 13 build path.
- Prototype the conversational shell as an ordinary application inside that desktop.
- Add a small set of useful system actions with visible results and failure handling.
- Make the conversational shell an optional session entry, then evaluate it as the default.
- Replace inherited components incrementally as the NordOS interfaces become clear.

This repository records the project direction and source foundation. These features are planned; the initial repository setup does not implement a new operating-system image or agent runtime.
