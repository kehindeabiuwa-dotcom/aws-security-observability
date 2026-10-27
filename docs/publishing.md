# Publish on GitHub and Dev.to

1. Create a **public** repository named **`aws-security-observability`** under **`kehindeabiuwa-dotcom`**, using **`main`** as the default branch.
2. Upload this folder's **contents** to the repository root, including `diagrams/`, `screenshots/`, `docs/` and `.github/`. The root should contain `README.md`, not another nested project folder.
3. Open [the repository](https://github.com/kehindeabiuwa-dotcom/aws-security-observability) and follow its article links. GitHub articles use relative paths, so images and navigation stay with the repository.
4. Open [the architecture image](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/architecture.png). This is also the hosted image location used by the Dev.to drafts; it becomes available after the upload.
5. For each file in `docs/articles/devto/`, create a Dev.to post. Set its title, description, tags, series and cover image from the YAML front matter, then paste the article body below the closing `---`. Preview the cover, screenshots and article navigation before publishing. `published: false` keeps imported drafts unpublished until you choose to publish them.
6. Publish the four articles in numbered order. Previous/next links already point to the corresponding GitHub articles, so they work independently of Dev.to post URLs.

The prepared URLs use the repository name above and the `main` branch. Keep these names when uploading so no link edits are needed. Original PDF links point to the cloud-portfolio repository.

## Editing diagrams

Open `.drawio` files in diagrams.net. Keep the matching SVG and PNG exports updated when editing the design. Dev.to uses PNG exports; GitHub includes the images in the repository.

## Reuse

The [MIT License](../LICENSE) allows reuse of the code and original documentation. Source-PDF references and screenshot provenance are listed in [the source map](source-map.md).
