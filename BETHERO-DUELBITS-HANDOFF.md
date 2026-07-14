# BetHero — Duelbits Reskin (Figma Handoff)

All work for this branch lives in **Figma**, not this repo. This file is the persistent record so any future session can pick up.

- **Figma file:** `gXIOm44SHag7BHJSvWs6dw` ("DUELBITS Monkeytilt - App UI - BetHero")
- **Figma auth:** `vlad@titansolutions.gg` (Titan Solutions team). Higgsfield = `admin@bethero.gg` account only.
- **MCP permission:** the Figma connector prompts on every call in web sessions. There is no in-session "always allow"; set auto-approve at the environment/permission level in the web UI (a gitignored `.claude/settings.local.json` does not persist across ephemeral containers).

## Pages
- **Page 1** (`0:1`) — original Monkey Tilt source. **Untouched** (reference).
- **DuelBits** (`40006064:10256`) — working reskin page (7 screens). Section `40006064:10257`.
- **Page 1 — Duelbits** (`40006155:11960`) — full mirror board cloned from Page 1 with reskinned screens swapped in. Section `40006155:10256`. **Primary deliverable.**

## Brand values
- **Duelbits green:** `#33C16C` (rgb 51,193,108) — from emblem.
- **Dark navy background:** `#0F171F` (rgb 15,23,31). Header bar `#213241` (rgb 33,50,65).
- **Duelbits emblem** (vector, 32×32): node `40006120:12308`.
- **New pack foil image hash:** `eb6b4b5e` (old Monkey Tilt foil was `b15f2e4d`).
- **Duelbits footer nav image hash:** `5a0d936b`.

## Work completed
1. New Duelbits header + footer applied across all screens (both boards).
2. Monkey Tilt logo → Duelbits emblem on all packs (browse packs, gold lobby packs, opening pack), keeping foil + event photos.
3. New Duelbits green pack foil (`eb6b4b5e`) applied to all pack backgrounds.
4. Pack bottom date text: black → white.
5. Full "Page 1 — Duelbits" mirror board built from Page 1 (connectors/labels intact; Page 1 untouched; Monkey Tilt originals hidden, never deleted).
6. All yellow/gold brand placeholder → Duelbits green; yellow-on-black screen backgrounds → dark navy. Applied to both the mirror board and the working DuelBits page.

## Open / optional
- Reward Unlocked/Locked cards were gold "treasure" style; under "any yellow → green" they are now green — revert to gold if desired.
- Full parity of the working DuelBits page with the mirror's new pack foil + white dates (currently the mirror is the most complete).
