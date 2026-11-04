# Upstream history and licenses

NordOS begins as a fork of [cutefishos/cutefish-core](https://github.com/cutefishos/cutefish-core), with related desktop, application, and distribution repositories maintained separately. The repository name changed to NordOS; the core's source history and its upstream fork relationship remain intact.

The initial source collection is recorded in `components.json`. Each entry identifies the original source, its verified fork when available, its default branch, a starting commit, and GitHub's detected license label.

## Fork setup status

Nine component forks were created and verified. GitHub then blocked further repository creation with “You have created too many repositories, too quickly. Please try again later.” Thirteen entries remain marked `pending_github_creation_limit`. Their upstream URLs and starting commits are recorded; the manifest does not claim those forks exist.

Forks were requested with all branches rather than only the default branch. The new project documents are the initial NordOS changes; the inherited core implementation remains available under its existing source layout. Its original README is preserved as `README.Cutefish.md`.

## Licensing inventory

The core, toolkit, framework, compositor, most applications, installer, and build guide report BSD-3-Clause at the repository level. The terminal and icon repositories report GPL-3.0. Wallpapers reports `NOASSERTION`; Plymouth theme and packaging have no detected repository-level license in GitHub's metadata.

These labels are inventory data. The actual license files, source headers, bundled dependencies, and asset attributions remain the source of the terms for each component. Packaging documents package-specific licenses in its `debian/copyright` files. The unknown or undetected entries need file-level review before deciding what to redistribute in a NordOS image.

The existing root `LICENSE` is retained for the inherited core repository. It does not relabel every component or bundled dependency as BSD-3-Clause. Preserve upstream license files and attributions as implementations are adapted or replaced.

## Keeping upstream available

For each local checkout, keep `origin` pointed at the NordOS project fork and add the original repository as `upstream`:

```sh
git remote add upstream https://github.com/cutefishos/COMPONENT.git
git fetch upstream
```

Review incoming changes on a development branch before integrating them with NordOS changes. Keep upstream provenance visible while replacement components are developed.

This project is independently maintained and is not presented as an official Cutefish release.
