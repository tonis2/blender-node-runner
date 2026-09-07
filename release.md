## Node libraries

Node Runner can now browse **node setups hosted in git repositories**.

- Add repositories under `Edit > Preferences > Add-ons > Node Runner`. The URL field accepts
  `owner/repo`, a GitHub page URL, a raw URL, GitLab, any static host, or a local folder.
- Browse them from the **Node Runner** tab in the sidebar (`N`) of the 3D viewport or a node
  editor: search by name, description or tag, filter by repository and by Shader / Geometry,
  in a grid or list view with pagination.
- **Apply to the selected object** from the viewport, or drop nodes into the tree you are
  editing from a node editor.
- Everything is **cached to disk**, so the panel fills instantly and keeps working offline.
- Private repositories are supported with an optional access token.

### Publishing

Two tools write and maintain `config.json` for you, under **Author Library** in the sidebar,
in the node editor right-click menu, and in the preferences:

- **Publish Selected Nodes** — export what you have selected into a library folder.
- **Generate config.json for a Folder** — index a folder of setups you already exported.

## Security

- Node setups fetched from a repository no longer reach the legacy `pickle` decode path, which
  executed arbitrary code. Pasting a string yourself is unchanged.
- Image file paths in remote setups are stripped before the setup is built.
- Compressed payloads are bounded while decoding.

## Fixes

- Confirming the Blender version-mismatch dialog no longer raises `AttributeError` when the
  import was started from the 3D viewport.

## Changed

- Removed the **Import at Cursor** and **Select Imported Nodes** preferences. Both defaulted to
  on and are now simply how import behaves.
