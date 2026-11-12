# NordOS development VM

The amd64 development disk boots the reorganized NordOS foundation using a Debian 13 base. It starts a local development account in the Wayland desktop with File Manager, Settings, and a terminal. Use a copy of the QCOW2 disk as the boot drive so the original stays available for a fresh start. The tested QEMU configuration uses a Q35 machine, BIOS boot, 4 GB of memory, Virtio graphics and storage, and user-mode networking.

With QEMU and its GTK and Virtio display modules available on the host, run:

```sh
cp NordOS_Development_0.1_amd64.qcow2 NordOS_Working.qcow2
./distribution/image/run-vm.sh NordOS_Working.qcow2
```

The development disk logs in automatically. Use the locally supplied development password for administrative actions. The image includes a compiler, Git, and CMake. Building the full system from within the VM also requires the development SDK and the dependencies in the [build guide](../../docs/BUILDING.md).

## Ownership of the boot platform

| Layer | Current implementation | Where a replacement belongs |
| --- | --- | --- |
| NordOS composition | Selected toolkit, framework, services, compositor, shell, File Manager, Settings, and resources | [Composition manifest](../composition.json) and `system/` |
| Image assembly | Debian cloud disk, Debian packages, cloud-init, and a systemd graphical boot | [Debian image backend](debian/) |
| Linux integration | Linux kernel, logind, DRM/KMS, libinput, udev, D-Bus services, and POSIX paths | `system/platform/linux` and the platform-specific portions of the inherited components |

Changing distributions primarily means supplying a new base image, dependency mapping, boot configuration, and service setup. A Linux distribution can share platform adapters where it provides their expected interfaces. The first replacement test should run the same desktop smoke checks against a different Linux base without changes to NordOS service policy.

Changing kernels requires a separate platform effort. The current power interface and Linux process implementation show where to place adapters. The compositor still relies on Linux DRM/KMS, device discovery, seat access, and input. Services and libraries also rely on logind, systemd user scopes, D-Bus providers, udev, and Linux filesystem and event behavior. Define the operations and results NordOS needs, adapt the inherited code at those boundaries, and test an end-to-end slice such as input, a graphical session, and shutdown on the second platform. Use existing kernel interfaces where they can implement that contract. Compatibility for existing Linux applications is a separate requirement. See the [architecture draft](../../docs/SYSTEM_ARCHITECTURE.md).

The current image is intended for development in a VM. USB installation, physical hardware, upgrades and recovery, and a complete build from inside the guest remain separate milestones.

The exported disk passed `qemu-img check` and cold booted without its provisioning media. The checks covered an active Wayland session, wired DHCP and DNS, system service status, package integrity, and write access to `/Applications` for the development user. File Manager, Settings, and the Xwayland terminal opened on the test desktop. The exported disk uses automatic local login with password-protected administration. The Linux Virtio GPU driver logged a warning during shutdown after the filesystems were unmounted. The VM powered off successfully, and the exported disk's checksum was unchanged.
