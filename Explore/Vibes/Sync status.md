# Sync status

**Status:** public experiment, version 0.1.0, self-hosted modified stack.

[Sync status](https://sync-status-vibe.aintnostressin.com/home) compares a user's latest Homeserver event cursor with the last cursor processed by Nexus. It displays syncing, delayed, and unreachable states and polls faster after writes. Its Nexus fork adds the required user-cursor endpoint, so this is not a standard-stack feature.

Sources: [Vibes board](https://vibes.pubky.app), [App fork](https://github.com/aintnostressin/pubky-app/tree/feat/sync-status-indicator), [Nexus fork](https://github.com/aintnostressin/pubky-nexus/tree/feat/user-cursor-endpoint).
