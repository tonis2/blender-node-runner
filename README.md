# Node Runner

A **Blender add-on for sharing node setups** — as plain text you can paste anywhere, or through
a node library hosted in a git repository.

Works with **Shader** and **Geometry** node trees, on Blender 4.5 and later.

#### Example of exporting and importing shader nodes

https://github.com/user-attachments/assets/ea813ab1-0408-41d4-8273-a8ba4953d2e2

## Features

### Import & export

- **📤 Export** the selected nodes to the clipboard or a file.
- **📥 Import** them back from the clipboard or a file, added alongside your existing nodes.
- **Four formats** — a compact base64 *Hash* for chat and comments, plus readable **JSON**,
  **AI JSON** and **XML** for anything that wants to diff or generate them.
- **Geometry Nodes aware** — modifier input values travel with the setup, so a re-import
  reproduces the look the author had, not just the interface defaults.
- **Applies to nothing?** If the node editor is empty, Node Runner creates the material or the
  Geometry Nodes modifier on your active object for you.
- Warns when a setup was exported from a different Blender version.

### Node library

Point the add-on at one or more git repositories of node setups and browse them from Blender:

- **Search** by name, description or tag, filtered by repository and by Shader / Geometry.
- **Grid or list view**, with pagination.
- **Apply to the selected object** from the 3D viewport, or drop nodes straight into the tree
  you are editing from the node editor.
- **Works offline** — everything is cached to disk, so the panel fills instantly and stays
  usable with no network. Refresh re-pulls.
- **Private repositories** are supported with an optional access token.

Repositories are plain git — no server, no account, no service in the middle.

## Installation

Grab the `.zip` from [Releases](https://github.com/tonis2/blender-node-runner/releases) and
install it with `Edit > Preferences > Add-ons > Install from Disk`, or clone this repository
into your Blender `extensions/user_default/` (or `scripts/addons/`) folder.

Then enable **Node Runner** under `Edit > Preferences > Add-ons`.

## Usage

### Sharing a single setup

- **Export** — select nodes, right-click > `Node Runner` > *Copy to Clipboard* or *Save to File*.
- **Import** — right-click > `Node Runner` > *Paste from Clipboard* or *Open File*.

### Using a library

1. `Edit > Preferences > Add-ons > Node Runner`, press **+** and paste a repository URL.
2. Open the **Node Runner** tab in the sidebar (`N`) of the 3D viewport or a node editor.
3. Press **Refresh**, search, and hit **+** on a setup to add it to your scene.

The URL field is forgiving. All of these work:

```
tonis2/blender-nodes                                  owner/repo shorthand
https://github.com/tonis2/blender-nodes               a normal GitHub page
https://github.com/tonis2/blender-nodes/tree/dev/lib  a branch, or a subfolder
https://raw.githubusercontent.com/…/main              an already-raw URL
https://gitlab.com/tonis2/blender-nodes               GitLab
https://example.com/nodes/                            any static host
/home/you/blender-nodes                               a local folder
```

### Publishing your own library

A library repository is a folder of exported setups plus a `config.json` index. You never have
to write that index by hand:

- **Publish Selected Nodes** — exports what you have selected and adds it to a folder's
  `config.json`.
- **Generate config.json for a Folder** — scans a folder of setups you already exported and
  writes the whole index at once.

Both live under **Author Library** in the sidebar, in the node editor right-click menu, and in
the add-on preferences. Commit and push the result; that is the whole publishing step.

## Documentation

Full documentation, including the `config.json` schema, is in [`docs/index.md`](docs/index.md).

To build it locally:

```bash
pip install mkdocs mkdocstrings-python mkdocstrings mkdocs-material
mkdocs serve
```

## Development

1. Clone this repository into your Blender `extensions/user_default/` folder.
2. Open Blender, go to `Edit > Preferences > Add-Ons`, search for `Node Runner`, enable it.

Run the test suite from the repository root — it uses a mocked `bpy`, so Blender is not needed:

```bash
pytest
pylint $(git ls-files '*.py')
```

## Credits

Originally created by [Noah Thiering](https://github.com/Noah4ever). This is an independent
continuation with the node library added.

## License

Released under the [GNU General Public License v3.0 or later](LICENSE).

---

Issues and contributions welcome. Happy blending 🔥
