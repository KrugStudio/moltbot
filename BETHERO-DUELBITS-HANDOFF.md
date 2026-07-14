# BetHero — Duelbits Reskin (Figma Handoff)

Single source of truth for resuming this work. All design work lives in **Figma**, not this repo.

## Access & accounts
- **Figma file:** `gXIOm44SHag7BHJSvWs6dw` ("DUELBITS Monkeytilt - App UI - BetHero")
- **Figma auth:** `vlad@titansolutions.gg` (Titan Solutions team). Verify with the Figma MCP `whoami` before editing.
- **Higgsfield:** `admin@bethero.gg` (the `higgsfield-bethero` account) ONLY — never rtrivv.
- **Dan's brandbook (comments):** file `xNVaqSRAbtCDcdPoMLgQYF` (needs FIGMA_TOKEN, not persisted here).
- **Related workspaces** (on the operator's local machine, NOT in cloud containers): `~/development/bethero/`, `~/Documents/Bethero/`, and the **mem-palace** notes. A fresh cloud session cannot read these; connect to them only in an environment where they are mounted, otherwise treat Figma + this file as the source of truth.

## Permission setup (Figma MCP)
- Web/mobile sessions prompt on every Figma call because `~/.claude/launcher-settings.json` only pre-approved `Skill`.
- Fix applied: added `mcp__127b415e-eef2-435e-afba-99710501b7ef` and `mcp__Figma` to `permissions.allow` in launcher-settings.json + project `.claude/settings.local.json` + project `allowedTools`. **Loads at session start** — a fresh session should be prompt-free for Figma.
- Full "bypass permissions" mode can only be enabled by the operator in the app's permission-mode control (an agent cannot self-enable it — safety guardrail).

## Pages
- **Page 1** (`0:1`) — original Monkey Tilt source. **Untouched** (reference).
- **DuelBits** (`40006064:10256`) — working reskin page (7 screens). Section `40006064:10257`.
- **Page 1 — Duelbits** (`40006155:11960`) — full mirror board cloned from Page 1 with reskinned screens swapped in. Section `40006155:10256`. **Primary deliverable / most complete.**

## Brand values
- **Duelbits green:** `#33C16C` (rgb 51,193,108).
- **Dark navy background:** `#0F171F` (rgb 15,23,31). Header bar `#213241` (rgb 33,50,65).
- **Duelbits emblem** (vector, 32×32): node `40006120:12308`.
- **Pack foil image hash:** NEW green `eb6b4b5e` (old Monkey Tilt foil `b15f2e4d`).
- **Duelbits footer nav image hash:** `5a0d936b`.

## Work completed (both boards unless noted)
1. New Duelbits header + footer across all screens; Monkey Tilt operator nav bars hidden.
2. Monkey Tilt logo → Duelbits emblem on all packs (browse, gold lobby packs, opening pack); foil + event photos kept.
3. New green pack foil (`eb6b4b5e`) applied to all pack backgrounds.
4. Pack bottom date text: black → white.
5. Built full "Page 1 — Duelbits" mirror board from Page 1 (connectors/labels intact; Monkey Tilt originals hidden, never deleted; Page 1 untouched).
6. All yellow/gold brand placeholder → Duelbits green; yellow-on-black screen backgrounds → dark navy. Applied to the mirror board AND the working DuelBits page.

## Method notes (for consistent edits)
- Non-destructive: hide, never delete (Monkey Tilt originals are hidden layers).
- Yellow detector (catches bright + dark gold, excludes green/cream/purple): `b<0.4 && r>0.25 && g>0.2 && (min(r,g)-b)>0.12 && r>=g*0.9 && g>=b*1.4 && |r-g|<0.45`. Full-screen gold (≥350×600) → navy; smaller gold → green. Recolor solids, strokes, and gradient stops; scope to effectively-visible nodes only.
- Leaderboard reskin overlays are Section-level siblings (instances can't take children).

## Open / next
- **Reward Unlocked/Locked cards** are now green (were gold "treasure" style) — revert those to gold if the operator prefers.
- **Working DuelBits page** has green+navy but NOT yet the newest pack foil + white dates — bring to full parity with the mirror if desired.
- Optional: read Dan's brandbook comments (needs FIGMA_TOKEN in ~/.zshrc).

## Repo
- Branch: `claude/bethero-duelbits-reskin-lrah3b`. No code changes — only this handoff file. All design changes are in Figma.
