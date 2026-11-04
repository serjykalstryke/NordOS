# Snap desktop integration

Snap application discovery is implemented in the NordOS project's
[toolkit component](https://github.com/serjykalstryke/cutefish-toolkit), rather
than duplicated in the session or launcher. Its integration commit is recorded
in the toolkit entry of `components.json`; the baseline field continues to
record the original fork snapshot.

The [toolkit pull request](https://github.com/serjykalstryke/cutefish-toolkit/pull/1)
contains the implementation and regression tests.

## Behavior

The toolkit's shared data-location list includes `/var/lib/snapd/desktop`.
The application registry therefore scans and watches
`/var/lib/snapd/desktop/applications`, and icon lookup also includes Snap's
exported icon directory. Absolute icon paths into `/snap/<name>/current` are
preserved. The executable lookup also checks `/snap/bin`, so a bare Snap
command in `TryExec` is recognized.

The existing Flatpak export directories and native application directories
retain their order, with Snap's export directory appended after them. User
application entries still take precedence. The change retains Cutefish's
fixed-location policy; it does not begin reading arbitrary `XDG_DATA_DIRS`
or `PATH` values.

The registry uses the desktop files exported by snapd directly. Installing,
refreshing, and removing a Snap uses the existing directory watches, including
when its application directory first appears. There are no copied launcher
files to become stale and no synchronization service to install.

## Build and runtime

Build and install the patched toolkit before the desktop components, following
the normal build order in [BUILDING.md](BUILDING.md). It changes the shared
base library; restarting just a store does not reload that library in the
already-running compositor and application runtime. Log out and log back in
after installing the updated package. Do not restart the compositor during
an active session with unsaved work.

The machine also needs a working snapd installation and mounted Snaps. For
a Debian development installation, install snapd through the distribution's
package manager, then follow snapd's setup instructions for the system.
The launcher change does not install snapd, alter confinement, grant extra
permissions, or configure application-specific interfaces or portals.

## Validation

The toolkit's existing base test executable contains two new regression tests:

- `ApplicationRegistryTest.IncludesSnapExportsAfterNativeAndFlatpakEntries`
  checks the actual launcher search path and its precedence.
- `ApplicationRegistryTest.TracksSnapExportInstallRefreshAndRemoval`
  starts with a missing export directory, installs a representative snapd
  desktop entry, verifies its command arguments, absolute icon path and
  window-class matching, then verifies a refresh and removal are noticed.

Run these alongside `ApplicationRegistryTest.*`, `DesktopEntryTest.*`,
`PathsTest.*`, the file-watch tests and MIME tests. The search-path test fails
against the unmodified toolkit.

For desktop validation after logging in again:

1. With Snap App Center installed, confirm that App Center appears in the
   launcher with its icon. Its exported desktop ID is `snap-store_snap-store`.
2. Open it from the launcher and confirm that an application window appears.
3. Install a desktop Snap through the store and check its icon appears without
   another login. Confirm it launches and can be pinned to the dock.
4. Refresh the app, then remove that test app and confirm its launcher entry
   disappears. Keep the App Center installed if it is the selected store.
5. Confirm existing native and Flatpak launcher entries are still present.

Discovery can be verified independently of launching an app. A Snap that
appears but fails to run still needs its snapd, confinement, graphics, or
portal problem diagnosed separately.
