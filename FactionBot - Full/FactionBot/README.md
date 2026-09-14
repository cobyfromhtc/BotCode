# FactionBot (BotCode) — Discord Ticket System

A self-contained **discord.py 2.x** bot with a full Ticket Tool–style ticket
system: panels, forms, claiming, automation, transcripts, SLA, analytics,
CSAT, escalation, canned replies, pause/resume, and more — all Discord-native
(no web dashboard, no AI).

## Requirements
- Python 3.10+
- A Discord bot token

## Setup
1. Create a `.env` file in the project root (or `tokens.txt`):
   `BOT_TOKEN=YOUR_BOT_TOKEN_HERE`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the bot:
   `python PythonFiles/Bot.py`
   (or use the launcher in `Bat Files/`)

The SQLite database (`data/bot_data.db`) is created and migrated
automatically on first start.

## Running MULTIPLE Bots (ModBot / TicketBot / UtilityBot + your own)

The project can run as **several Discord bots at once** — each with its own
token, its own entry file, and its own slice of the features. All bots share
the same database, so panels, tickets and settings work across all of them.

**How to add bots — you only edit `tokens.txt` (or `.env`):**

```
# ONE bot that does everything:            fill in BOT_Token, run Bot.py

# The 3 standard bots (any subset):        fill in the lines you want,
ModBot_Token=YOUR_MODERATION_BOT_TOKEN     then run RunBots.py
TicketBot_Token=YOUR_TICKET_BOT_TOKEN
UtilityBot_Token=YOUR_UTILITY_BOT_TOKEN

# ADD MORE bots (any name), 2 lines each:
FunBot_Token=YOUR_TOKEN
FunBot_Cmds=poll,giveaway,endgiveaway      <- commands MOVED to FunBot
```

Then start everything:

```
python PythonFiles/RunBots.py
```

Notes:
- **Any subset works** — configure only `TicketBot_Token` for a dedicated
  tickets-only bot, etc.
- **Extra bots = two lines**: a `<Name>Bot_Token` and a `<Name>Bot_Cmds`
  list. The listed commands move to your new bot from the standard bot that
  normally runs them. You can also use `ModBot_Cmds=...` to move commands
  between the standard bots. A custom bot with a token but no valid commands
  refuses to start (with instructions) instead of sitting online empty.
- **Comma-separated list** instead of named tokens:
  `BOT_TOKENS=modToken,ticketToken,utilityToken` (assigned to Mod, Ticket,
  Utility in that order; extras ignored).
- `RunBots.py` supervises the bots: it restarts a crashed bot (up to 5×) and
  Ctrl+C stops all of them. Each bot logs to its own file
  (`bot-mod.log`, `bot-ticket.log`, `bot-utility.log`, `bot-fun.log`, …).
- One bot per domain: extra tokens after a comma on a named line are ignored.
- Invite every configured bot to your server; each one serves only its own
  commands (slash + prefix), so nothing double-responds. Chained commands
  (`!ban @user, !close`) split correctly across the bots that own them.
- Custom bots also **inherit the background jobs** of any standard bot they
  replace: run only `FunBot` with the utility commands and it handles
  welcomes, XP, giveaway endings, etc.
- Single full bot unchanged: set `BOT_TOKEN` and run `Bot.py` as before.

## Feature Overview

### Panels & Ticket Creation
- `/panel` — interactive panel builder (embed, button, settings, category,
  support role, two-step close toggle)
- `/multipanel` — up to 25 panels in ONE message (Ticket Tool "Attached
  Panels"), configurable buttons-per-row
- `/dropdownpanel` — select-menu panel where each option opens a different
  panel
- `/reactionpanel` — reaction-based panels (react with an emoji to open)
- `/panelquestion` — up to 5 form questions asked before creation
- `/new` / `/ticket` — command-style tickets (staff can open on behalf)
- Multi-embed panel messages (`/panelembed*`), panel refresh (`/panelupdate`)
- Business hours per panel (`/schedule`), ticket numbering with zero padding
  and naming templates (`/naming`)

### Ticket Management
- Claiming with advanced policy (`/claim`, `/unclaim`, `/claimconfig`):
  auto-replace, owner-claim, rename/move/hide-on-claim, claimer-only actions
- `/close` (with rating prompt), `/closerequest` (alias `!ca`),
  two-step close with Reopen/Delete/Transcript moderator buttons
- `/add` / `/remove` — users AND roles
- `/rename`, `/move`, `/priority`, `/note` / `/notes`
- `/pause [30m|1h|2d|1w|indefinite]` / `/resume` — suspend ALL automations
  for a ticket (timers shift so paused time doesn't count)
- `/private` / `/unprivate` — standalone private-ticket toggle
- `/rate` — manually send the CSAT prompt (one rating per ticket)
- `/ticket-info` — full status embed (priority, claim, SLA, automation
  state, participants, age, activity, escalations)
- Escalation routes + history (`/escalate`, `/escalateroute`,
  `/escalationhistory`)

### Transcripts & Logging
- HTML transcripts with DB backup fallback, `/transcript [channel] [lines]`
- Transcript automation (`/transcriptconfig`): save modes, DM on close,
  archive channel, plain-text format, no-attachment mode
- Ticket log channel with per-event toggles (`/ticketlog`): created, closed,
  reopened, renamed, deleted, transcript, claim, unclaim, priority

### Automation Engine (`/automate`)
- Triggers: created, closed, reopened, owner_left, close_request, claim,
  unclaim, delayed, no_response
- Actions: close, delete, claim, unclaim, add/remove role, send message
  (ticket / transcripts / **DM the creator**), rename, move, escalate,
  execute command, start/stop automation
- Conditions: subject, priority, category, claim state, ticket count,
  creator, hour of day, weekday
- Persisted timers that survive restarts

### Limits & Guardrails
- Global per-user limit, per-panel limit, closed-ticket limit, all-users
  open cap, limit bypass roles (`/limitbypass`)
- Idle auto-close (panel + guild fallback), first-response SLA with breach
  warnings (`/slaconfig`), channel recycling, overflow-safe analytics

### Knowledge & Responses
- `/canned` — canned replies with autocomplete: `add`, `send`, `edit`,
  `delete`, `list` (variable support: `{ticket.user}`, `{panel.name}`, …)
- `/kb` — knowledge base with search + auto-suggestions in tickets
- `/customcommand` — custom commands with automation action lists
- Support flows (`/flow`) with branching + application review queues
  (approve/reject buttons, auto-decision deadlines)

### Analytics & Ops
- `/analytics`, `/csat`, `/staffstats`, `/staffanalytics`, `/ticktrends`,
  `/responsedistribution`, `/export` (CSV)
- `/ticketdebug`, `/permissionlevel`, `/tickethelp`, `/dbcleanup`
- Localization (`/locale`), branded replies (`/brandedreplies`), staff
  discussion threads (`/staffthread`), thread tickets (`/threadtickets`)

## Project Layout
```
PythonFiles/
  Bot.py                  # core bot + ticket system (hybrid commands)
  TicketTool/             # premium feature package (26 modules)
  ReactionRoles/          # reaction roles package
data/bot_data.db          # SQLite (auto-created)
```

## Notes
- Slash commands for the premium/package features and newer ticket commands
  are guild-scoped to the configured home guilds (Discord's 100-global-command
  limit); prefix (`!`) versions work everywhere.
- Requires the Manage Channels permission for most staff commands; see
  `/permissionlevel` for the access model.
