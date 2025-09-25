# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository provides a reusable GitHub Actions workflow for automatically building and pushing Docker images to Docker Hub. It supports two different project structures:

1. Projects with a single Dockerfile in the root directory (e.g., li88iioo/Photonix)
2. Projects with multiple Dockerfiles in different subdirectories (e.g., JefferyHcool/BiliNote)

## Code Architecture

The system consists of two main workflow files:

1. `.github/workflows/docker-build.yml` - The core reusable workflow that handles the actual Docker build and push operations
2. `.github/workflows/main.yml` - The main workflow that defines which repositories to build

### Key Features

- Supports both single and multiple Dockerfile projects
- Configurable Dockerfile path and build context
- Automatic tag generation with date stamps and latest tags
- Reusable workflow design

## Common Development Tasks

### Adding New Repositories

To add a new repository to the build process, add a new job in `main.yml`:

```yaml
  # Build new project
  build-new-project:
    uses: ./.github/workflows/docker-build.yml
    with:
      source_repo: 'username/repository'
      docker_image_name: 'image-name'
      # If Dockerfile is not in root, specify path
      dockerfile_path: 'path/to/Dockerfile'
      context_path: 'path/to/context'
```

### Modifying Build Parameters

The reusable workflow supports several parameters:
- `source_repo`: Required Git repository to check out
- `docker_image_name`: Required Docker Hub image name
- `dockerfile_path`: Optional Dockerfile path (defaults to "Dockerfile")
- `context_path`: Optional build context path (defaults to ".")

### Testing Changes

To test changes to the workflows:
1. Make changes to the workflow files
2. Commit and push to trigger the scheduled builds
3. Or manually trigger the workflow through the GitHub Actions interface