# Sorting the system into NordOS architecture

Working draft • Updated November 11, 2026

## Direction and decision status

**Agreed direction.** Establish the structure of the operating system first. Reuse the Cutefish toolkit and useful essential implementations within NordOS's design. Application porting follows this work. The unit of sorting is a responsibility, which may occupy only part of an existing repository.

The design bible establishes first-class directories, files, and applications, a source-agnostic `.app` model, platform services, a replaceable Linux backend, and AI that supports direct user intent. The referenced design conversation also distinguishes the **System Library**, which supplies the tools and instructions for running programs and their dependencies, from dependencies supplied by applications. It calls for sharing dependencies without unnecessary duplication and transferring an application between NordOS systems without separately installing its dependencies.

**Proposed architecture.** The component boundaries, source directories, and storage names below put those principles into an initial structure. They remain proposals. This document maps source responsibilities and identifies further refactoring. The initial core reorganization is implemented as described below. Complete target boundaries and a NordOS image remain to be built.

This is the immediate direction for development. It supersedes the package-profile work as the next milestone and defers the design bible v0.3's suggested first application port. The earlier profile remains an integration experiment. Upstream Cutefish improvements remain useful and should continue where the work is shared.

## Implemented foundation

The first source pass now places the inherited core under `system/library`, `system/services`, `system/desktop`, and `system/platform/linux`. Linux power requests have an explicit NordOS interface, and the session consumes a build-time component selection. Existing installed paths and service identifiers remain compatible. The [build guide](BUILDING.md) records the actual tree and commands.

The distribution driver composes the modified core with selected, pinned Cutefish sources and stages installation separately. The full core has compiled and staged successfully. Several inherited components still mix responsibilities, so a source move is not evidence that every boundary is complete. File Manager and toolkit service extraction remain subsequent work.

## The system's parts

| NordOS part | Responsibility | Starting material |
|---|---|---|
| **System Library** | The programming contract for NordOS. Defines file, directory, application, and resource concepts, GUI controls, service clients, and the interfaces for loading and running software. | Cutefish toolkit UI and reusable base interfaces, framework file abstractions and service clients. |
| **System Services** | Own system operations and authoritative state. Manage sessions, files, applications, permissions, preferences, devices, power, and operation results. | Parts of `cutefish-core`, application discovery code in the toolkit, and service logic currently spread through framework clients and frontends. |
| **Desktop** | Present and manipulate the system's objects. Own window interaction, desktop surfaces, search, launcher, dock, system controls, and user-facing prompts. | Cutefish compositor and shell, File Manager's desktop view, Settings views, authorization and notification views. |
| **Platform** | Supply host-specific mechanisms behind NordOS interfaces. Linux is the first implementation, including its kernel and userspace integrations. | Linux/POSIX operations and integrations with systemd/logind, device services, graphics, audio, and authorization. |
| **Managed application dependencies and runtimes** | Store and supply versioned software required by applications, with explicit compatibility and ownership. | Existing dependency metadata and bundle handling as inputs. A complete shared dependency store remains to be built. |
| **Applications** | Represent complete user-facing functions with identity and lifecycle, presented as `.app` objects across sources. | Existing application discovery and bundle handling. Porting application payloads is deferred. |
| **Data** | Keep user documents, application state, system configuration, durable service state, and disposable caches under explicit ownership. | Existing file operations, XDG conventions, configuration files, and service-specific storage as migration inputs. |

The System Library is the public contract and reusable implementation. System Services enforce operations and own state. For example, a library client can request a power change while a service applies session policy and a Linux adapter asks logind to perform it. These are logical boundaries. They need not each become a separate process or package.

Execution support crosses these boundaries deliberately. The System Library exposes the tools and contracts for running software, System Services own launch policy, and execution adapters implement native, Linux, Wine/Proton, or Mac/Reef behavior. Versioned runtime artifacts belong to managed dependency storage. An execution adapter contract remains to be designed.

AI belongs in this structure as a system service with a desktop interface. It receives permission-scoped observations and uses the same actions as graphical controls. The services validate and authorize actions independently. Direct search, launch, file operations, and settings remain usable when AI is unavailable.

## Applications, tasks, and system capabilities

**Agreed principle.** An application is distinct from the task it helps accomplish. File Manager is the user-facing surface for understanding and working with saved data. It obtains information from other parts of the system and renders that information as navigable objects. The system's file and directory concepts exist independently of this particular application.

Here, surface means presentation and interaction. Cutefish also uses its File Manager process to render desktop icons, which is a separate implementation detail. An application can present system concepts while retaining its own identity, interaction design, and lifecycle.

**Proposed division of responsibility.** File Manager owns its browsing experience, views, selection, and task coordination. The System Library exposes the shared file, directory, and application contracts. System Services own operations and authoritative state where shared coordination or privilege is needed. Platform implementations supply the underlying storage mechanisms. A file picker, search interface, or authorized AI client can consume those same capabilities without requiring File Manager to be running.

This is a logical separation. An interface may be implemented by an in-process library, a service, or a kernel facility as appropriate. Process boundaries and communication methods remain engineering choices. Applications can contain substantial domain logic while relying on common system capabilities. Dependency completeness includes the declared platform contract.

**Proposed review test.** Replacing the File Manager should preserve access to saved data, the meaning of file and directory objects, and permission enforcement. Views should reflect the observed result of an operation, including changes made through another client. Current Cutefish coupling must be assessed before claiming this behavior is implemented.

## Sorting the code we already have

Paths in this table identify the original Cutefish source locations used for the mapping. The implemented core paths are recorded in the build guide. The table remains the responsibility map for subsequent extraction.

| Existing source | NordOS destination by responsibility | Work needed |
|---|---|---|
| Toolkit `src/ui/` | System Library → UI | Retain controls and reusable interaction primitives. Define which behavior is guaranteed by NordOS. |
| Toolkit `src/base/`, `src/gpu/`, `src/wayland/` | System Library interfaces and Platform implementations | Separate reusable contracts from epoll, inotify, sd-bus, process, rendering, and Wayland mechanisms as each interface is extracted. |
| Toolkit `src/base/application_registry.*`, `application_bundle.*`, `desktop_entry.*`, `mime_apps.*` | System Library → application objects and clients. System Services → inventory, associations, and lifecycle. | Preserve discovery behavior while establishing one authoritative application model for all consumers. A `.desktop` entry is input metadata, not a universal identity scheme. |
| Framework `files/` | System Library → file and directory interfaces. System Services → file operations and volumes. Platform/Linux → implementation. | Split reusable file behavior from POSIX filesystem and UDisks integration. Preserve existing ownership and file-operation semantics. |
| Framework `clients/` | System Library → service clients. Platform/Linux → host service adapters. | Separate client contracts from direct NetworkManager, BlueZ, UPower, AccountsService, and other host-specific calls. |
| Core `session/` | System Services → session orchestration | Keep login-session startup, shutdown ordering, and restart policy together. Extract the hard-coded selection of desktop processes into an explicit composition. |
| Core `session/power.*` | System Services → power contract. Platform/Linux → logind adapter. | Separate the action interface from the logind transport while preserving interactive authorization and error reporting. |
| Core `appruntime/`, `common/runtime_client.*` | System Services → application execution. System Library → execution client. | Separate application identity and launch policy from process creation and systemd scopes. This daemon is not a shared dependency store. |
| Core `common/detached_process.*`, `appruntime/applicationscope.*` | Platform/Linux → process implementation | Contain Linux process tracking and systemd-specific behavior behind execution interfaces. |
| Core `applicationsfolder/` | System Services → application placement and installation authority | Preserve privileged publication rules. Treat `/Applications` as placement, with identity, acquisition, and runtime selection separately defined. |
| Core `cutefish-services/` | System Services → appearance, clipboard, power, permissions, language, and diagnostics | Name the owners of each responsibility. Keep its present shared process initially where useful. Separate policy, prompts, and host mechanisms within it. |
| Core `locales/`, `privacy/` | System Services → language/privacy policy. Platform/Linux → privileged implementation. | Isolate locale generation, camera/device access, and host configuration changes from their public requests. |
| Core `polkit-agent/`, permission and crash dialogs | Desktop → system prompts. Platform/Linux → authorization transport. | Keep UI separate from authority. A prompt displays a decision request, while the responsible service enforces it. |
| Compositor `src/shell/`, `src/switcher/`, authentication views | Desktop → shell and system views | Reorganize launcher, dock, status/control surfaces, notifications, wallpaper, and lock interaction around NordOS behavior. |
| Compositor `src/wm/`, `src/scene/`, `src/render/`, `src/wayland/`, `src/input/`, `src/display/` | Desktop → window system | Retain working window and display behavior while defining the contract used by the shell and clients. The compositor remains essential infrastructure. |
| Compositor `src/backend/`, `src/xwayland/`, `src/auth/pam_backend.cpp` | Platform/Linux → display/input/session/authentication. Execution integration → Linux/X11 compatibility. | Reuse existing backend seams. Keep platform handles and host authentication details inside implementations. |
| File Manager `src/desktop/` | Desktop → desktop surface | Separate its persistent desktop role from its file-browsing application role. Session startup currently relies on this implementation. |
| File Manager browsing views | Applications → File Manager frontend, using System Library file interfaces | Present system-provided file, directory, and application objects. Keep browsing and interaction behavior with the application while shared capabilities have independent owners. |
| File chooser views | System Library → reusable selection UI, with desktop integration where required | Use the same file and directory contracts as File Manager. Whether the chooser is embedded or service-hosted remains an implementation decision. |
| Settings UI | Desktop → settings surfaces | Let the relevant service own each setting and its validation. A control panel is a client of those services. |
| Portal and screen recording implementations | System Services → mediated file/device/capture access. Platform/Linux → portal and PipeWire integration. | Preserve permission enforcement and existing callers while exposing the underlying capabilities consistently. |
| App Center acquisition backend | System Services → source adapters | Existing providers cover Debian, Flatpak, Snap, and AppImage. Future pip and Homebrew providers follow the same separation from identity and execution. |
| Compositor `src/computer_control/` and computer-use bridge | System Services → observation/action capabilities. Desktop → consent and interaction surfaces. | Reuse supported control mechanisms. Future AI orchestration is a separate consumer of these capabilities. |
| Icons, wallpapers, translations, standard themes | System resources | Classify by owner and update lifecycle. Preserve original licenses and attribution. |
| Packaging and installer projects | Distribution tooling | Build, install, update, and recover the selected system composition. Package boundaries can differ from architecture boundaries. |

Several existing components span categories. In particular, the toolkit contains host mechanisms, the compositor composes shell and display infrastructure in one process, and File Manager supplies part of the desktop. Sorting requires separating responsibilities inside those components.

## Proposed source organization

This tree describes source ownership within the NordOS project. It does not prescribe installed filesystem paths or require importing every fork into one repository. Selected sources can remain in their upstream repositories while the build records their ownership and pinned versions.

```text
NordOS/
  system/
    library/
      objects/              file, directory, application, resource contracts
      ui/                   toolkit and common controls
      clients/              clients for system services
    services/
      session/
      files/
      applications/         inventory, identity, lifecycle
      libraries/            dependency ownership and runtime selection
      settings/
      permissions/
      devices/              network, audio, displays, input, power
      intelligence/         intent, context, authorized action coordination
    desktop/
      shell/
      window-system/
      system-views/         settings, prompts, file selection
    adapters/
      sources/              acquisition and source ownership
      execution/            native, Linux, Wine/Proton, Mac/Reef
    platform/
      linux/                kernel and host-userspace implementations
    resources/
  applications/             future first-party application work
  distribution/             image, package, installation and recovery tooling
  tests/
  docs/
```

The source adapter answers how software is obtained and maintained. The execution adapter answers how its implementation runs. The platform adapter supplies the underlying host mechanisms. These boundaries allow the same application object to work across different combinations.

## Sorting the installed system and its data

The same ownership model should shape what the user sees on disk. The following names are candidate locations, with implementation and migration still open.

| Proposed logical home | Contents and owner |
|---|---|
| `/System/Library` | NordOS platform interfaces, toolkit, clients, and execution support supplied by the OS. |
| `/System/Services`, `/System/Desktop`, `/System/Platform` | OS-owned service implementations, desktop components, and host backend. |
| `/System/Resources` | OS-owned static assets. |
| `/Library/Libraries`, `/Library/Runtimes` | Managed, versioned shared dependency and runtime contents. Their identity is distinct from the platform contract in the System Library. |
| `/Applications`, `~/Applications` | Shared or personal application objects. Existing source managers retain ownership of their payloads. |
| Per-user application state | Settings, profiles, databases, and writable execution state, keyed by the relevant application/profile identity. Exact paths remain open. |
| User directories | Documents and other user-owned files, independently accessible from the application that created them. |
| System state, configuration, caches, and transient state | Separate stores according to lifetime, owner, and recovery behavior. Exact NordOS paths remain open. |

Logical homes do not yet require moving Linux-managed files. The initial backend can retain `/usr`, `/etc`, `/var`, `/run`, and existing user locations while the model assigns ownership and services resolve locations. Whether the visible homes become physical directories, managed views, or a combination is an open design decision. A directory rename alone does not establish the service or kernel boundary.

A dependency store must preserve each application's required versions. Copying a `.app` with references to a source machine's store is insufficient for the requested flash-drive behavior. The eventual copy mechanism must carry the required dependency contents to a compatible target. Materializing shared contents during copy or using transparent filesystem sharing are possible mechanisms. Neither is selected here. Source licensing, architecture compatibility, and platform-version requirements must be represented before promising portability.

Installed runtime code and writable runtime state have different owners and lifetimes. For example, shared Wine software is a runtime, while an application's writable prefix may contain its settings, installed components, and documents. Preserve such contents until they can be classified safely.

## First structural changes

1. **Assign owners.** Use this map to label current source responsibilities, callers, privileges, state, and update authority. Keep the inherited build working while making these boundaries explicit.
2. **Extract a small platform boundary.** Start with session power actions. Keep shutdown/session policy in the service, place the request contract in the service interface, and place logind calls in `platform/linux`. Preserve the distinction between an accepted request and an observed completed state. Check authorization, failure reporting, and callers before expanding the pattern.
3. **Make session composition explicit.** Describe which component supplies the compositor, desktop surface, and session services. Preserve readiness, trusted connections, restart behavior, and shutdown order. Then NordOS can substitute implementations deliberately.
4. **Separate shared models from desktop views.** Establish file/directory and application service ownership used by the shell, file views, Settings, and future AI consumers. Define the System Library contract around the capabilities actually implemented.
5. **Give system software and state explicit homes.** Centralize location resolution and ownership. Implement the chosen layout in a disposable image once compatibility and migration behavior are defined.
6. **Build the reorganized system.** Verify session startup, file operations, settings, display/input, permissions, and recovery through the new boundaries. Application ports and additional execution environments follow this foundation.

The first engineering milestone is a working system with identifiable NordOS responsibilities and an exercised platform boundary. Source moves must update build definitions and tests together. Each extraction should preserve its current behavior before changing the user experience.

## Decisions still open

- The final names and granularity of System Library and service interfaces.
- Which logical components share a process, repository, or update unit.
- Whether `/System` and `/Library` are physical locations or managed views, and how package-managed software participates.
- The guaranteed base platform capabilities versus separately managed libraries and runtimes.
- The identity, permission, and persistence contracts used by all system consumers.
- The boundary between built-in file/settings surfaces and ordinary applications.
- How ordinary bundle copying carries shared dependencies across filesystems.
- The supported first system composition and its build environment.

## Evidence and scope

This mapping uses the local NordOS core checkout and the reviewed Cutefish toolkit, framework, compositor, File Manager, and App Center sources. It draws product principles from the design bible and the referenced “NordOS Design Philosophy” conversation, including David's later System Library discussion. This thread supplies the immediate system-first correction. Detailed paths and mechanisms above are proposals, not additional user decisions.

The initial core source reorganization and staged build are implemented. The [development VM](../distribution/image/README.md) boots the composition on the Debian 13 image backend. That backend owns image assembly and distro-specific provisioning. Linux kernel and userspace integration still span the compositor, framework, toolkit, and services. Installed-system migration and replacement platforms remain open.
