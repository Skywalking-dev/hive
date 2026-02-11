---
description: Manage Vercel deployments, logs, and environment
argument-hint: <logs|deployments|env> [project] [options]
---

Interact with Vercel projects using the vercel skill.

> [!IMPORTANT]
> Follow the rules in the [vercel] skill.

# Usage

## Logs
- `logs <deployment>` - view deployment logs
- `logs <project> --prod` - view production logs

## Deployments
- `deployments <project>` - list recent deployments
- `deployments <project> --status` - check deployment status

## Environment
- `env <project>` - list environment variables
- `env <project> <key>` - get specific variable

# Prerequisites
- Vercel CLI installed and authenticated
- `VERCEL_TOKEN` in `.env` for API access
