# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository provides a reusable GitHub Actions workflow for automatically building and pushing Docker images to Docker Hub. It supports two different project structures:

1. Projects with a single Dockerfile in the root directory (e.g., li88iioo/Photonix)
2. Projects with multiple Dockerfiles in different subdirectories (e.g., JefferyHcool/BiliNote)

## Code Architecture

The system consists of two main workflow files:

1. `.github/workflows/docker-build-reusable.yml` - The core reusable workflow that handles the actual Docker build and push operations
2. `.github/workflows/main.yml` - The main workflow that defines which repositories to build using matrix strategy

### Key Features

- Supports both single and multiple Dockerfile projects
- Configurable Dockerfile path and build context
- Automatic tag generation with date stamps and latest tags
- Matrix-based builds for multiple repositories
- Reusable workflow design

## Common Development Tasks

### Adding New Repositories

To add a new repository to the build process:

1. For single Dockerfile projects, add a new entry to the matrix in `main.yml`:
   ```yaml
   - repo: 'username/repository'
     image_name: 'image-name'
   ```

2. For multiple Dockerfile projects, add separate entries for each Dockerfile:
   ```yaml
   - repo: 'username/repository'
     image_name: 'image-name-component1'
     multi_dockerfiles: |
       [{"path": "component1/Dockerfile", "context": "component1"}]
   - repo: 'username/repository'
     image_name: 'image-name-component2'
     multi_dockerfiles: |
       [{"path": "component2/Dockerfile", "context": "component2"}]
   ```

### Modifying Build Parameters

The reusable workflow supports several parameters:
- `source_repo`: Required Git repository to check out
- `docker_image_name`: Required Docker Hub image name
- `dockerfile_path`: Optional Dockerfile path (defaults to "Dockerfile")
- `context_path`: Optional build context path (defaults to ".")
- `multi_dockerfiles`: Optional JSON array for multiple Dockerfiles

### Testing Changes

To test changes to the workflows:
1. Make changes to the workflow files
2. Commit and push to trigger the scheduled builds
3. Or manually trigger the workflow through the GitHub Actions interface