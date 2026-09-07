# 🔗🏃 Node Runner

## ✨ Introduction

**Node Runner** is a Blender add-on for sharing node setups. It serializes the nodes you select
into a portable document — optionally compressed and base64-encoded into a single short string —
which can be pasted into a chat message, committed to a repository, or read back by another tool.

It works with both **Shader** and **Geometry** node trees, and targets Blender **4.5 and later**.

Beyond one-off sharing, Node Runner can browse **node libraries hosted in git repositories**:
a folder of exported setups plus a `config.json` index, searchable and applicable from Blender's
sidebar.

## 🌟 Features

### Import and export

- **📤 Export** the selected nodes to the clipboard or to a file.
- **📥 Import** from the clipboard or a file. Imported nodes are *added* to the current tree;
  nothing existing is replaced.
- **📄 Context menu integration** in the Shader and Geometry node editors.
- **Geometry Nodes modifier values** are captured on export and restored on import, so a setup
  reproduces the author's look rather than bare interface defaults.
- **Automatic target creation** — importing into an empty editor creates a material or a
  Geometry Nodes modifier on the active object.
- **Version awareness** — every export records the Blender version it came from, and import
  asks for confirmation when it differs.

### Node library

- **Multiple repositories**, each with its own branch and optional access token.
- **Search** across name, description, id and tags, with repository and Shader / Geometry filters.
- **Grid or list view**, with pagination (20 per page by default).
- **Apply to the selected object** from the 3D viewport, or into the tree you are editing from
  a node editor.
- **Offline disk cache** — the panel is populated from disk at startup and keeps working with
  no network. Downloads are lazy and cached.
- **Authoring tools** that write and maintain `config.json` for you.

## 📦 Export formats

| Format | Extension | Use it for |
| --- | --- | --- |
| **Hash** | `.txt` | The default. zlib-compressed, base64-encoded, prefixed `Name__NR…`. Short enough for a chat message or a YouTube comment. |
| **JSON** | `.json` | Readable and diffable. The right choice for a library repository in git. |
| **AI JSON** | `.json` | A compact, named-socket variant that reads well for humans and language models. |
| **XML** | `.xml` | A type-tagged document, for tooling that prefers XML. |

Import auto-detects the format, so you never have to say which one you are pasting.

## 🚀 Usage

### Exporting

1. Select the nodes you want in a Shader or Geometry node editor.
2. Right-click to open the context menu and choose **Node Runner**.
3. Pick **Copy to Clipboard** or **Save to File…**.
4. Set a name and format in the dialog, then confirm.

### Importing

1. Right-click in the node editor and choose **Node Runner**.
2. Pick **Paste from Clipboard** or **Open File…**.

Nodes land at your mouse cursor and are left selected, ready to move as a group.

If the editor has no tree at all, Node Runner creates one on the active object: a new material
for a shader setup, or a Geometry Nodes modifier for a geometry setup.

### Browsing a library

1. Open `Edit > Preferences > Add-ons > Node Runner`.
2. Press **+** to add a repository and paste its URL.
3. Open the sidebar (`N`) in the 3D viewport or a node editor and select the **Node Runner** tab.
4. Press **Refresh**, then **+** on any result to apply it.

In the 3D viewport, applying builds a fresh tree on the **selected object**. In a node editor,
it drops the nodes into the tree you are currently editing.

## 🔗 Repository URLs

The URL field accepts several forms and normalizes them to a raw-content base. The resolved
address is shown beneath the field so mistakes are visible immediately.

| You type | It resolves to |
| --- | --- |
| `tonis2/blender-nodes` | `https://raw.githubusercontent.com/tonis2/blender-nodes/main` |
| `https://github.com/tonis2/blender-nodes` | the same |
| `https://github.com/tonis2/blender-nodes/tree/dev/lib` | that branch and subfolder |
| `https://github.com/…/blob/main/nodes/a.json` | the containing folder |
| `https://raw.githubusercontent.com/…/main` | used as-is |
| `https://gitlab.com/tonis2/blender-nodes` | `https://gitlab.com/tonis2/blender-nodes/-/raw/main` |
| `https://example.com/nodes/` | used as-is — any static host works |
| `/home/you/blender-nodes` | a local folder, handy for testing before you push |

A branch named in the URL wins over the **Branch** field.

> **Private repositories**
>
> Tick **Private Repository** to reveal the token field. Public repositories need no
> credentials. Because `raw.githubusercontent.com` does not accept an `Authorization` header,
> a GitHub repository with a token configured is read through the Contents API instead.
>
> Blender stores add-on preferences unencrypted, so the token is kept in plain text on disk.

## 📁 The `config.json` schema

A library repository is a folder of exported setups plus an index at its root:

```json
{
  "schema": 1,
  "name": "Tonis Node Library",
  "description": "Procedural vines, ropes and fences",
  "entries": [
    {
      "id": "climbing-vine",
      "name": "Climbing Vine",
      "description": "Ivy that grows over a surface, with leaf scattering.",
      "file": "nodes/vine_nodes.json",
      "tree_type": "GeometryNodeTree",
      "tags": ["vine", "plant", "organic"],
      "author": "tonis2",
      "blender_version": "5.2.0",
      "updated": "2026-09-07",
      "thumbnail": null
    }
  ]
}
```

**Required per entry:** `id` (a slug, unique within the repository), `name`, and `file`
(a path relative to `config.json`, so both flat and nested layouts work).

**Optional:** `description`, `tree_type` (`GeometryNodeTree` or `ShaderNodeTree` — omit it and
the entry shows under every type filter), `tags`, `author`, `blender_version`, `updated`.

`thumbnail` is **reserved and currently ignored**; it is parsed and preserved so a future
release can use it without breaking existing repositories.

Unknown keys, at both the top level and inside an entry, are ignored and preserved. A single
malformed entry is skipped with a warning rather than blanking the whole repository.

## ✍️ Publishing a library

You never have to write `config.json` by hand. Both tools live under **Author Library** in the
sidebar, in the node editor right-click menu, and in the add-on preferences.

### Publish Selected Nodes

Exports what you have selected and inserts or updates the matching entry in a folder's
`config.json`, creating the file if it does not exist. Keys you added by hand are preserved on
update. Defaults to JSON format, and leaves image paths out — absolute paths point at your own
machine and are useless to anyone else.

### Generate config.json for a Folder

Scans a folder of setups you have already exported and writes the whole index at once. Entry
ids come from **file names**, so two setups exported under the same name cannot collide. Display
names prefer the export name, falling back to a tidied file name when the export only carries a
default label like `MyNodes`.

**Update Existing Entries** is off by default, so re-running it after adding files only appends —
descriptions and tags you wrote by hand are never overwritten.

Then commit and push. That is the entire publishing step; there is no server involved.

## 🗃️ Cache

Downloaded indexes and setups are cached under Blender's user data directory (or the extension's
own user directory when installed as an extension). The panel reads this cache at startup, so it
never touches the network while drawing.

**Refresh** re-pulls each index, using `ETag` so an unchanged repository costs almost nothing.
Setup files are re-downloaded only when their entry changes. **Clear Cache** in the preferences
discards everything.

## 🔒 Security

Node setups fetched from a repository are decoded with the legacy `pickle` fallback **disabled**,
and any image file paths they carry are stripped before the setup is built. Entry paths that are
absolute or try to escape the repository are rejected, and cached files are named from the entry
id rather than from anything the repository controls.

Pasting a string yourself is unchanged — that path still accepts legacy exports.

## 🔄 Changes in 1.5

**Added**

- The node library: repositories, the sidebar browser, search and filters, grid and list views,
  pagination, the offline cache, and the two authoring tools.
- Geometry Nodes support throughout, including modifier values.
- JSON, AI JSON and XML export formats alongside the original hash string.

**Removed**

- The **Import at Cursor** and **Select Imported Nodes** preferences. Both defaulted to on and
  are now simply how import behaves: pasted nodes land at the cursor and end up selected. Turning
  the second one off never restored your previous selection anyway — it just left nothing
  selected — so nothing of value is gone.
- The link to the former `node-runner.thiering.org` sharing site, which this add-on never talked
  to. Library repositories replace it.

## ⚠️ Troubleshooting

**"config.json not found — check the URL and branch"**
The repository is reachable but has no index at that path. Check the branch, and remember
`config.json` has to be committed and pushed — not just generated locally.

**"Access denied (401)" or "(403)"**
A private repository needs **Private Repository** ticked and a valid token.

**"Online access is disabled in Preferences > System"**
Blender's *Allow Online Access* is off, or it was started with `--offline-mode`. Cached
setups still apply.

**"Cannot add Geometry Nodes to a … object"**
The active object cannot carry a Geometry Nodes modifier. Select a mesh, curve, point cloud,
volume or grease pencil object.

**A setup imports but does not look right**
Check the version warning. A setup exported from a different Blender version may reference
sockets or properties that have since changed.

## 🚧 Limitations

- External assets such as image textures are not embedded. Exports can record absolute paths for
  local sharing, but library entries deliberately omit them.
- Imported nodes are added to the current tree; nothing existing is replaced.
- Thumbnails are not implemented yet. The grid shows a type icon in the slot reserved for them.
