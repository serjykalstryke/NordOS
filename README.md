# NordOS

[Working state](docs/WORKING_STATE.md) covers the current foundation and the Typewriter USB build.

NordOS Design Bible • First draft • Version 0.3 • November 10, 2026

This README presents the design bible. Standalone copies are available in [Markdown](docs/DESIGN_BIBLE.md) and [Word](docs/NordOS_Design_Bible.docx). Repository setup, component inventory, and license links follow the design sections.

**Current work — system architecture first.** The core is now organized under NordOS's System Library, System Services, Desktop, and Linux Platform source areas, with an extracted power interface and explicit session composition. The [system architecture draft](docs/SYSTEM_ARCHITECTURE.md) maps existing code to those responsibilities and records proposed source and installed-system layouts. It supersedes the first-app-port and package-profile sequencing below. Application porting follows the system foundation. The v0.3 bible remains a design snapshot. [Build the current foundation](docs/BUILDING.md) or inspect the [pinned system composition](distribution/README.md).

## Purpose and decision status

The [development VM guide](distribution/image/README.md) shows how to run the first bootable foundation and where the Debian and Linux platform dependencies belong.

NordOS aims to be a human-centered desktop operating system whose concepts remain coherent across software sources, execution environments, and eventually kernels. Users should work with directories, files, and complete applications while the system manages the machinery needed to make those applications function.

This bible preserves direction while leaving implementation choices open. It is a working basis for design and engineering review, not a claim that the architecture is implemented or approved in full.

**Agreed principle** means a direction stated by David in the available conversation. **Requested goal** means a direction explicitly included in the brief for this draft, whose earlier discussion is not present in the retrieved reference. **Proposed architecture** means a mechanism suggested in the conversation or developed here to realize those goals. **Open question** means a decision still needed. Assistant suggestions do not become agreed decisions merely by appearing in the source.

## 1 Human experience comes first

**Requested goal — GUI first, function first, human centered.** Design around what people are trying to accomplish. The graphical interface should be a complete, understandable way to carry out ordinary work, including installing software, finding files, changing settings, and recovering from errors. Users should not need terminal commands to complete normal desktop tasks.

Function determines structure and interaction. Visual simplicity should come from clear concepts and useful defaults, rather than hiding essential controls. A polished screen is incomplete if the underlying operation is unreliable, inaccessible, or difficult to recover from.

**Proposed design rules.** Use the same names and behaviors across the shell, File Manager, App Center, Settings, and application dialogs. Make progress, consequences, failures, and recovery visible in language people understand. Preserve keyboard access and accessibility alongside pointer interaction. Offer advanced controls when they serve a real task; graphical completeness need not eliminate command-line or automation interfaces.

**Review test.** Can a person discover the action, understand its effect, complete it, and recover from a failure using the graphical interface? If not, the feature is not yet complete under this goal.

## 2 Directories files and applications are first class

**Requested goal.** Directories, files, and applications each deserve explicit treatment in the user experience and platform model. Directories organize user-controlled material. Files are persistent resources people can create, open, move, share, and retain. Applications are complete units of functionality with identity and lifecycle.

An executable file is not automatically a complete application. A directory containing software may implement an application bundle, but the user-facing application should have a coherent identity beyond its current filesystem location. Conversely, presenting a bundle as one application should not make ordinary user documents disappear into opaque application storage.

**Agreed principle — the application folder.** NordOS adopts `.app` as its bespoke application folder. A bundle may contain a NordOS-native, Linux, Mac, or Windows application. The same application concept applies across those implementations; the folder suffix does not determine which execution environment is required.

**Agreed principle — first class and source agnostic.** The application folder gives an application distinct, first-class status alongside files and directories. Its identity and user-facing behavior should remain coherent regardless of its acquisition source. A source determines how software is acquired, installed, and updated; it does not define what an application is. NordOS preserves source ownership and provenance while presenting the application as a manageable object.

**Proposed architecture.** File Manager understands application bundles as applications while providing an intentional way to inspect their contents. Launchers and file associations refer to registered applications rather than guessed executable paths. Application registration records supported document types, entry points, and available actions.

**Open questions.** Which operations should behave like ordinary file operations for a bundle? When does moving or copying one require installation, validation, or repair? How should scripts, portable tools, services, and command-line utilities appear without misclassifying every executable as a desktop application?

## 3 Installation should produce a complete application

**Agreed principle.** Aim for “clean installation of as many applications as possible.” An application made for another operating system especially benefits from being managed as “one package.” The intended outcome is a working, understandable application rather than a collection of exposed prerequisites.

**Requested goal — dependency closure.** Every required application component must either belong to the bundle or be an explicit dependency supplied through a managed runtime or platform contract. Functional completeness does not require physically copying every dependency into every bundle.

**Proposed architecture.** Represent the application as a logical bundle containing or referencing executables, resources, dependency versions, launch configuration, permissions, and its execution environment. Track which resources are exclusive, shared, or user-owned. Separate the portable application concept from any particular archive or on-disk layout.

Shared runtimes should have explicit identity and version compatibility rules. Multiple versions may coexist when applications require them. The manager should retain a runtime while any installed application needs it and reclaim it only when it is no longer referenced. An application update must not silently replace another application's required environment.

**Proposed bundle contract.** Build on Cutefish's existing bundle support, extending it with native launch and managed execution environments. A NordOS `.app` should describe its identity, entry point, processor architecture, execution environment, and required private or shared dependencies. A native executable, Windows executable, or Mac executable can occupy the application payload without changing the outer application model. The internal directory names, metadata format, and compatibility markers are not yet finalized.

The proposed installation locations are `/Applications` for shared applications and `~/Applications` for personal applications. A compatible runtime may be managed outside the bundle and referenced explicitly; a Windows bundle need not carry a separate copy of Wine. Mutable application state and user documents remain separate as described in section 6.

Source adapters still own source-specific installation rules. Adopting `.app` does not authorize moving APT, Flatpak, or Snap files out of locations their managers require. How these installations participate in the application-folder model needs an explicit integration design. An imported Mac `.app` also needs validation and a supported execution environment; its suffix alone does not establish that it follows the NordOS bundle contract.

**Proposed lifecycle expectations.** Validate dependencies before registering an installation as ready. Make interrupted operations recoverable. Keep enough installation information to explain what is installed and why. Where a source cannot provide transactional updates or complete ownership records, expose that limitation and offer a supported recovery path rather than claiming stronger guarantees.

**Open questions.** What belongs in the base platform versus a runtime? What version constraints are supported? Who supplies security updates for pinned components? What can be deduplicated safely? When can offline installation or export include every dependency, and what redistribution restrictions apply?

## 4 Application identity is separate from its source

**Agreed principle.** App Center must not remain locked to APT or .deb files. It should work with the host's appropriate software tools and be able to reach sources such as pip and Homebrew where useful.

The `.app` application-folder model and source agnosticism are complementary. An acquisition format such as `.deb` describes how software arrives and is managed by its source; a NordOS `.app` describes the application object presented by the system. Source adapters connect those concepts without requiring every source to adopt the same archive format or relocate its managed files.

**Requested goal.** Present unified application identity across APT/deb, Flatpak, Snap, AppImage, pip, Homebrew, and future sources. These names describe acquisition or packaging mechanisms, not the application's meaning to the user.

**Proposed architecture.** Maintain distinct records for the application identity, a particular build or implementation, an installation, its source, and its execution environment. A single identity may have several implementations and installed variants. Preserve source provenance and variant differences even when the default interface groups them together.

An identity record could hold a stable identifier, publisher information, display metadata, and document associations. An installation record could hold source-specific identifiers, version, architecture, channel, location, dependencies, and update authority. These are candidate fields, not a finalized schema.

Applications with similar names must not be merged automatically. Cross-source equivalence needs trustworthy publisher identifiers, curated mappings, or explicit user decisions. A Windows and native implementation may be related without sharing compatible settings, licenses, plugins, or data formats.

### Source adapter responsibilities

**Proposed architecture.** Each adapter translates discovery, metadata, installation, updates, removal, and inventory into source-specific operations. It reports its capabilities and limitations through a common contract. APT may initially be the first complete adapter; additional adapters should not require rewriting the App Center interface.

The common application service owns normalized identity and lifecycle records. Adapters preserve the source's dependency and ownership rules. They must not delete package-managed files behind another manager's back. External changes made through native tools require inventory reconciliation.

pip and Homebrew can supply libraries and tools as well as applications. Only suitable entries should be promoted to application objects. A proposed pip strategy uses managed environments rather than changing the system Python environment. Exact isolation and policy remain open.

App Center is the graphical acquisition and management surface. It should consume shared services also usable by the launcher, Settings, and File Manager. Compatibility execution should not be implemented as App Center-only behavior.

## 5 Execution environments are a separate axis

**Agreed principle.** Extend the cohesive application model to Windows and Mac applications, building on the compatibility direction discussed around Wine, Proton, and Cutefish's Mac work. Acquisition and execution are related concerns but need not live in the same subsystem.

**Proposed architecture.** An execution environment provides preparation, launch, integration, diagnostics, and cleanup for an application implementation. The installation source does not by itself determine the execution environment. A single application identity can have implementations requiring different environments.

**NordOS native.** Target NordOS application and platform interfaces. The toolkit, API, ABI, and packaging contract require separate specifications; discussion of C++20 and Skia is architectural context rather than a newly ratified commitment here.

**Linux.** Support existing Linux applications on the initial Linux host. Over time, isolate their Linux-specific assumptions from NordOS-native contracts. Continued Linux application support on another kernel would require an actual compatibility implementation; a kernel abstraction alone does not supply it.

**Windows through Wine or Proton.** Manage compatible runtime versions, prefixes, required DLLs, overrides, and graphics translation settings as application environment resources. Prefer one understandable application over asking users to assemble those resources manually. The appropriate choice between Wine and Proton is workload-specific and remains a policy question.

**Mac through Reef or another suitable backend.** Preserve this as a compatibility direction and research track. Define support per application and backend capability. The draft makes no claim that arbitrary Mac applications already run, or that Reef is a settled execution contract.

**Proposed behavior.** Check prerequisites before launch. Show actionable failures and allow repair or environment selection when useful. Avoid automatic migration between implementations until data compatibility and rollback are understood. Runtime isolation, host integration, hardware access, and permissions must be designed explicitly; an application bundle is not by itself a security boundary.

## 6 Application bundles and application data

**Requested goal.** Separate installed software from mutable application state and user documents. Updating or removing code should not accidentally destroy the user's work.

**Proposed architecture.** Treat the bundle as managed software and environment definitions. Treat per-user application state as settings, profiles, databases, and other mutable information. Keep user-created documents under user control. Track caches and temporary material separately so they can be reclaimed without pretending they are durable data.

A compatibility prefix may mix installed software, registry configuration, settings, and documents. The implementation must classify or preserve those contents before promising clean separation. Some applications will need a coarse preserved state container rather than immediate fine-grained ownership.

**Proposed lifecycle policy.** Removing an application keeps user data by default and offers a clearly explained separate deletion choice. Backups distinguish software restoration from state restoration. Switching between source variants or execution environments requires a migration plan where state formats differ. Rolling back a bundle does not automatically roll back a migrated database.

**Open questions.** What constitutes an application instance: a process, a user profile, or an installed configuration? This draft uses “installation” and “per-user state” until that term is settled. How are multi-user data, secrets, cloud state, exports, and shared documents handled?

## 7 Platform services and a replaceable kernel

**Agreed principle.** Design early for Linux to “plug into” NordOS and potentially be replaced. Kernel independence is an architectural goal, not a commitment to build a new kernel immediately.

**Proposed architecture.** Applications and desktop components consume NordOS-defined services. Those services use an explicit kernel adaptation boundary. Linux is the initial backend. The contract describes capabilities NordOS needs rather than renaming Linux system calls.

Candidate service areas include application lifecycle and identity; storage and file access; permissions and credentials; processes and memory; interprocess communication; networking; graphics and display; devices and input; and power and session management. Ownership and API boundaries need focused design work rather than one large abstraction layer.

Keep Linux-specific handles and behavior inside implementations where practical. Application identity should not be a Linux process ID. Native public APIs should avoid unnecessary dependency on Linux filesystem layouts, device paths, or service-manager conventions. Existing Linux applications can continue to use those conventions through their supported environment.

A replaceable kernel requires more than process and memory wrappers. Drivers, graphics, synchronization, security semantics, networking, and compatibility backends must still work. Define capability discovery and conformance tests, then prove a narrow service slice on a second backend before claiming broad portability. Linux may remain the production kernel indefinitely if it continues to serve NordOS well.

## 8 Implementation roadmap

**Requested priority.** Current upstream Cutefish work comes first. NordOS is the guiding direction; it should not force a premature platform fork or kernel project. The phases below are proposals with exit criteria, not calendar commitments or statements of current implementation status.

### Short term strengthen upstream Cutefish

Continue useful upstream desktop, toolkit, shell, App Center, and reliability work. Inventory existing package-source logic and Linux-specific assumptions. Complete the App Center source abstraction incrementally, retaining a working APT path and validating it with one meaningfully different source.

Record AI interaction rules and prototype intent recognition in search without interrupting direct application launch. Draft the smallest common identity, installation, adapter, and lifecycle contracts. Establish graphical install, launch, update, removal, and error-recovery flows for a representative application. Record design decisions as work reveals constraints.

For the application-folder foundation, the proposed first implementation is one native Cutefish application packaged as a `.app`. Exercise discovery, launch, update, and removal in a baseline Cutefish development environment before extending the model to more applications and compatibility backends. The initial target is a usable NordOS foundation built from baseline Cutefish, rather than an exact replica of David's personal installation.

**Proposed exit criteria.** Two sources can participate without source-specific logic spreading through the interface. Installed applications have traceable ownership and provenance. The graphical lifecycle works, including a failed installation and retained user data after removal.

### Medium term establish shared application services

Move common lifecycle logic into reusable services. Add adapters according to actual user needs. Implement versioned runtime ownership, inventory reconciliation, and recoverable operations. Develop a limited Windows compatibility path around selected applications, with managed environment profiles and clear diagnostics. Prototype bundle and user-state separation.

Prototype permission-scoped AI context and a small set of verifiable system actions through shared services. Introduce NordOS service interfaces around the platform areas being actively changed. Keep Linux operational while measuring where assumptions leak through. Investigate Mac/Reef compatibility through bounded experiments rather than a universal-support promise.

**Proposed exit criteria.** A representative set of applications uses the same identity and lifecycle model across sources and at least one compatibility environment. Updating one application preserves another's runtime requirements. Removal and repair respect ownership and user data.

### Long term prove platform independence

Stabilize native application contracts once implementation experience justifies it. Expand compatibility where technically viable. Investigate safe export, restore, and migration between compatible installations or implementations. Study relevant ideas from OpenHarmony and other systems without assuming adoption of their architecture.

Prototype a second kernel backend for a small service slice. Evaluate driver and compatibility requirements before expanding. Decide whether replacing Linux delivers enough benefit to justify the cost; architectural freedom is valuable even without replacement.

**Proposed exit criteria.** The second backend demonstrates meaningful platform behavior through the same contracts. Supported capabilities and remaining gaps are documented. Kernel replacement and broad compatibility commitments follow evidence.

## 9 AI is native and respects user intent

**Agreed principle.** NordOS will be AI native, but AI will not be forced on the user. Intelligence should support the task the person is performing. It should not turn an ordinary interaction into an unsolicited conversation.

If someone uses search to find and open an application, the system should perform that task directly. AI should not interrupt, demand engagement, or insert an unrelated response. When the person asks a question, the system should recognize that intent, answer appropriately, and ask for more information when needed to understand or fulfill the request. Clarification should resolve meaningful uncertainty without becoming routine friction.

**Agreed principle — system awareness.** AI should be aware of relevant system state, available resources, installed applications, and other system details so it can make reliable and safe changes. That awareness is part of the operating system's architecture, rather than requiring the user to reconstruct the machine's context in every conversation.

**Proposed architecture.** Provide a shared intent and context service that distinguishes direct actions, application or file lookup, questions, and ambiguous requests. Preserve a direct path for ordinary search and launch. When intent is unclear and the possible actions have materially different consequences, ask a focused question before choosing one.

Supply current, permission-scoped context through platform services: application inventory and identity, runtime availability, storage and memory resources, operation progress, relevant settings, and diagnostic state. Distinguish observed facts from inference, and refresh relevant state before making changes. System awareness should not imply unrestricted access to personal files or secrets.

Route AI-initiated changes through the same managed application and system services used by the graphical interface. Those services should enforce permissions and validate operations independently of the AI's interpretation. Check prerequisites, preserve a recovery path where possible, and verify the resulting state before reporting success. The AI should explain consequential changes in understandable terms and request clarification or authorization when the task or its consequences require it; exact thresholds remain to be designed.

**Proposed review examples.** Searching for an installed application opens it without conversation. Asking why storage is low produces an answer grounded in relevant current information. An ambiguous request to remove something prompts a focused clarification if the target or treatment of user data is uncertain. An attempted change is reported as successful only after its outcome has been checked.

**Open questions.** How should search distinguish a question from a title that resembles one? How can people correct an intent classification or control AI participation? Which context is available by default, what stays on the device, and what requires explicit access? What operations require approval, which can proceed under an existing request, and how are actions recorded and undone? What direct search and system-management behavior remains available when AI is unavailable?

## 10 Principles for reviewing future decisions

Use these as draft review criteria derived from the goals above. They do not independently approve a particular mechanism.

- Start from the person's task and make ordinary operations complete in the GUI.
- Make AI native, respect direct user intent, and ground system changes in current state.
- Preserve directories, files, and applications as understandable, user-controlled concepts.
- Use `.app` as the application folder across native, Linux, Mac, and Windows implementations.
- Install complete functionality with explicit dependency ownership.
- Separate identity, acquisition, execution, and mutable data.
- Share runtimes deliberately while preserving application compatibility.
- Keep source provenance and capability limits visible where they affect a decision.
- Build compatibility into shared services so every desktop surface can use it.
- Define NordOS contracts early and prove abstractions incrementally.
- Advance upstream Cutefish now while preserving longer-term architectural options.

## 11 Decisions still needed

**Identity and trust.** Who allocates stable application IDs? What proves publisher identity and cross-source equivalence? How are forks, editions, channels, and simultaneous installations represented?

**Packaging and ownership.** What internal layout and metadata identify a NordOS `.app`, and how do imported Mac bundles retain their own conventions? How do existing package-managed installations participate in the application-folder model? Which dependencies can be shared? How are package-manager ownership conflicts resolved?

**Security and updates.** What permission and isolation model applies to each backend? Who updates shared and pinned runtimes? How are vulnerable dependencies, offline installs, and unsupported versions handled?

**Data and migration.** What is preserved on removal? How are state versions tracked? Which migrations are reversible? How are application state and user documents exposed for backup and inspection?

**Compatibility.** Which applications and workloads define initial success? What constitutes supported Wine, Proton, or Reef behavior? How will host integrations and unsupported features be communicated?

**Platform boundaries.** Which service contracts should be extracted first? What is guaranteed by the native API versus the ABI? Which second-backend experiment would best test kernel independence?

**AI behavior and authority.** How are intent, context access, action permissions, confirmation thresholds, privacy, recovery, and operation records specified? How is reliability tested when context is stale or a request is ambiguous?

**Governance and scope.** Which changes belong upstream in Cutefish, which are NordOS-specific, and what evidence warrants a fork? Who approves a proposal and maintains the decision record?

## 12 Maintaining this bible

Promote a proposal to an agreed decision only after explicit review. Record its date, rationale, consequences, and implementation evidence. Keep product intent separate from mechanisms so an implementation can change without losing the goal it serves.

A decision entry should contain an ID, subject, status, decision owner, date, rationale, affected interfaces, alternatives, and evidence. Suggested statuses are proposed, accepted, implemented, superseded, and rejected. Acceptance and implementation are separate milestones.

### Source record

Primary reference: David's conversation “NordOS Design Philosophy,” conversation ID 6af372c6-4fac-83e9-9a85-98419114f03b. Direct anchors are the goals of clean installation across sources, cohesive cross-platform applications, and early design for kernel replaceability. Additional coverage and the upstream Cutefish priority come from the November 10, 2026 drafting brief. David's subsequent November 10, 2026 direction establishes AI-native operation, optional user engagement, intent-sensitive search and answers, and system awareness for reliable and safe changes as agreed principles. Further direction selects baseline Cutefish as the initial NordOS foundation and adopts `.app` as the bespoke application folder for native, Linux, Mac, and Windows software. Detailed architecture and phase gates remain proposals unless explicitly labeled otherwise.

## Current foundation

This repository is a fork of **[Cutefish core](https://github.com/cutefishos/cutefish-core)**, renamed NordOS. It contains the reorganized session and system-services code, the initial NordOS platform boundary, source-composition tooling, and project documents. The original component instructions are preserved in [README.Cutefish.md](README.Cutefish.md).

The first-run setup experience, integrated assistant, system-state tools, alternative-desktop integration, and NordOS distribution image are planned work. Their direction is recorded in [docs/VISION.md](docs/VISION.md).

**Source setup status:** 19 of the original 22 component forks are verified as of November 10, 2026. Wallpapers, system-monitor, and calendar remain pinned to upstream commits while GitHub rejects further creation attempts. The current packaging pipeline also includes cutefish-webkit, which needs a separate source and build inventory entry. See [the initial release plan](docs/INITIAL_RELEASE.md).

## Repository guides

- [Foundation build and verification results](docs/FOUNDATION_STATUS.md)
- [System architecture and component sorting](docs/SYSTEM_ARCHITECTURE.md)
- [Standalone design bible](docs/DESIGN_BIBLE.md)
- [Editable Word design bible](docs/NordOS_Design_Bible.docx)

- [Project vision and incremental replacement strategy](docs/VISION.md)
- [NordOS system baseline and package profile](docs/SYSTEM_BASELINE.md)
- [Build baseline and development layout](docs/BUILDING.md)
- [Upstream history and license inventory](docs/UPSTREAM.md)
- [Machine-readable component inventory](components.json)

## Clone this starting point

```sh
git clone https://github.com/serjykalstryke/NordOS.git cutefish-core
git -C cutefish-core remote add upstream https://github.com/cutefishos/cutefish-core.git
```

The checkout name `cutefish-core` preserves the directory layout expected by the existing Cutefish packaging tools. Other components are separate repositories.

## Component collection

The inventory captures the starting commits on 2026-11-04. Forks keep their upstream history and branches. A pending entry links to the original source until its fork can be created.

| Component | Original source | NordOS project fork | GitHub license label |
|---|---|---|---|
| cutefish-core | [upstream](https://github.com/cutefishos/cutefish-core) | [NordOS](https://github.com/serjykalstryke/NordOS) | BSD-3-Clause |
| cutefish-toolkit | [upstream](https://github.com/cutefishos/cutefish-toolkit) | [cutefish-toolkit](https://github.com/serjykalstryke/cutefish-toolkit) | BSD-3-Clause |
| filemanager | [upstream](https://github.com/cutefishos/filemanager) | [filemanager](https://github.com/serjykalstryke/filemanager) | BSD-3-Clause |
| cutefish-compositor | [upstream](https://github.com/cutefishos/cutefish-compositor) | [cutefish-compositor](https://github.com/serjykalstryke/cutefish-compositor) | BSD-3-Clause |
| settings | [upstream](https://github.com/cutefishos/settings) | [settings](https://github.com/serjykalstryke/settings) | BSD-3-Clause |
| wallpapers | [upstream](https://github.com/cutefishos/wallpapers) | Pending GitHub creation limit | NOASSERTION |
| terminal | [upstream](https://github.com/cutefishos/terminal) | [terminal](https://github.com/serjykalstryke/terminal) | GPL-3.0 |
| cutefish-dm | [upstream](https://github.com/cutefishos/cutefish-dm) | [cutefish-dm](https://github.com/serjykalstryke/cutefish-dm) | BSD-3-Clause |
| icons | [upstream](https://github.com/cutefishos/icons) | [icons](https://github.com/serjykalstryke/icons) | GPL-3.0 |
| getting-started | [upstream](https://github.com/cutefishos/getting-started) | [getting-started](https://github.com/serjykalstryke/getting-started) | BSD-3-Clause |
| cutefish-framework | [upstream](https://github.com/cutefishos/cutefish-framework) | [cutefish-framework](https://github.com/serjykalstryke/cutefish-framework) | BSD-3-Clause |
| text-editor | [upstream](https://github.com/cutefishos/text-editor) | [text-editor](https://github.com/serjykalstryke/text-editor) | BSD-3-Clause |
| qt-plugins | [upstream](https://github.com/cutefishos/qt-plugins) | [qt-plugins](https://github.com/serjykalstryke/qt-plugins) | BSD-3-Clause |
| calculator | [upstream](https://github.com/cutefishos/calculator) | [calculator](https://github.com/serjykalstryke/calculator) | BSD-3-Clause |
| video-player | [upstream](https://github.com/cutefishos/video-player) | [video-player](https://github.com/serjykalstryke/video-player) | BSD-3-Clause |
| plymouth-theme | [upstream](https://github.com/cutefishos/plymouth-theme) | [plymouth-theme](https://github.com/serjykalstryke/plymouth-theme) | See upstream files |
| cutefish-installer | [upstream](https://github.com/cutefishos/cutefish-installer) | [cutefish-installer](https://github.com/serjykalstryke/cutefish-installer) | BSD-3-Clause |
| packaging | [upstream](https://github.com/cutefishos/packaging) | [packaging](https://github.com/serjykalstryke/packaging) | See upstream files |
| cutefish-computer-use | [upstream](https://github.com/cutefishos/cutefish-computer-use) | [cutefish-computer-use](https://github.com/serjykalstryke/cutefish-computer-use) | BSD-3-Clause |
| xdg-desktop-portal-cutefish | [upstream](https://github.com/cutefishos/xdg-desktop-portal-cutefish) | [xdg-desktop-portal-cutefish](https://github.com/serjykalstryke/xdg-desktop-portal-cutefish) | BSD-3-Clause |
| system-monitor | [upstream](https://github.com/cutefishos/system-monitor) | Pending GitHub creation limit | BSD-3-Clause |
| calendar | [upstream](https://github.com/cutefishos/calendar) | Pending GitHub creation limit | BSD-3-Clause |

## Implementation direction

Current upstream Cutefish work is the priority. The short, medium, and long term roadmap above guides incremental application services, AI integration, compatibility, and platform independence. Earlier assistant and setup sketches are retained in [the vision notes](docs/VISION.md); their mechanisms remain proposals.

The existing upstream Debian 13 build path is the initial development baseline. The long-term distribution base, implementation languages, and model providers remain open design decisions.

## Project notes

- [Snap desktop integration](docs/SNAP_SUPPORT.md) documents the toolkit change for discovering Snap applications, its runtime requirements, and validation steps.
- [MSI Raider audio workaround](https://github.com/serjykalstryke/msi-raider-linux-audio-fix) is a separately verified hardware repair. It is hardware-specific and is not installed globally by this repository.
- This repository retains the upstream core [BSD-3-Clause license](LICENSE). Each other component and its bundled dependencies retains its own license and attribution.
