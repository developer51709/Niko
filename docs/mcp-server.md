# Owner MCP server

The owner MCP server is the direct control surface for the production bot. It
authenticates with the database-backed owner key generated on the staff **MCP
Server** page and exposes status, logs, error reports, incidents and deployment
tools over `https://mcp.<site>/mcp`.

## Deploying a commit

Normal updates use **`niko_deploy_commit`**, not inline file content:

1. Commit and push the change to `main` on the Niko repository.
2. Copy the full commit SHA from `git rev-parse HEAD`.
3. Call `niko_deploy_commit` with that SHA.

The server fetches the commit's changed files from GitHub, verifies each file
against its Git blob SHA, and applies only paths in the updatable areas. Tests,
docs, workflows and other repository files are reported as skipped. The commit
SHA is immutable, so the update is reproducible even if `main` moves while it
runs.

Use the optional `paths` argument to apply only part of a commit. Entire commit
updates are refused above 250 files or 40 MiB, matching `niko_deploy`.

## Announcements with images

`niko_announce` accepts up to 10 optional `images`. Each image needs exactly
one of base64 `data` or a public `url`, plus an optional `filename` stem and
per-image `spoiler` flag:

```json
{
  "title": "A new release",
  "body": "The details live here.",
  "images": [
    {"url": "https://cdn.example/release.png"}
  ]
}
```

Niko downloads `url` images itself and uploads both URL and inline images as
real Discord attachments in the announcement's media gallery, so the delivered
message does not depend on the source link staying alive. The image type is
detected from the bytes, so `data` can also be a `data:image/...;base64,...`
URI. The 8 MiB per-image and 20 MiB total limits match staff broadcasts, and
URL downloads time out after 20 seconds. Announcement containers use no accent
colour, and the optional announcements ping is rendered in the footer.

`niko_deploy` still exists for small inline hotfixes, but it should not be used
for large files: every byte has to be escaped into one JSON-RPC request and the
whole request has to fit in the client's context.

## Configuration

| Variable | What it does |
| --- | --- |
| `GITHUB_REPOSITORY` | Repository to read commits from, in `owner/name` form. Defaults to `developer51709/Niko`. |
| `GITHUB_TOKEN` | Optional. Raises GitHub's API rate limit and allows reading a private fork. |

`niko_deploy_commit` keeps the same backups, syntax checks, area reloads and
rollback behaviour as `niko_deploy`; only the file source changes.

## Full deployments

Automatic Render deploys are disabled. Use the connected Render integration to
trigger and inspect a full deployment when the change needs a fresh process
image, new dependencies or a build step. Incremental MCP commits are for code
that the existing area reloaders can apply without restarting the service.
