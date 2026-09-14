# FactionBot

A self-contained **discord.py 2.x** all-in-one server-management bot built around
**six core systems** — all Discord-native (no web dashboard, no AI, no external
services):

| System | Highlights |
| --- | --- |
| 🎫 **Tickets** | Panels (button/dropdown/reaction/multi), forms, claiming, automation engine, SLA, CSAT, escalation, transcripts, canned replies, knowledge base, analytics |
| ✅ **Verification** | Persistent button panel, unverified/verified roles, account-age gate, timeout sweep (optional kick), join/verify logging |
| 📊 **Polls** | Native Discord polls, auto-ending, stored results with bar-chart announcements, history |
| 📈 **Invites** | Real join attribution (invite snapshots + vanity URLs), leaderboards, fake/bonus/left tracking, join announcements |
| ⭐ **Leveling** | MEE6-style XP curve, anti-farming (cooldown + duplicate detection), level role rewards, configurable announcements |
| 🛡 **AutoMod** | Rules engine: 11 rule types × combinable actions (delete/warn/strike/timeout/kick/ban/notify), exemptions, priorities, escalation, XP penalty |

Plus supporting infrastructure: reaction roles, sticky roles, warnings, temp
mutes, message logging, welcome messages, custom commands, branding, OWS owner
toggles, and a dynamic help system.

## Requirements
- Python 3.10+
- A Discord bot token (with **Server Members** + **Message Content** + **Presence** intents)

## Setup
1. Create a `.env` file in the project root (see `.env.example`):
   `BOT_TOKEN=YOUR_BOT_TOKEN_HERE`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the bot:
   `python PythonFiles/Bot.py`
   (or use the launchers in `Bat Files/`)

The SQLite database (`data/bot_data.db`) is created and migrated
automatically on first start. On first launch the bot DMs the owner a
step-by-step tutorial (re-send anytime with `!tutorial`).

## First-run flow

```
!csetup        ← start here: live status panel for every subsystem
!vsetup        ← verification: roles, panel, age gate, timeout
!panel         ← tickets: interactive panel builder
!invites setup ← invite tracking + join announcements
!level config  ← XP tuning · !level reward add 10 @Role
!automod add words delete badword1, badword*
!help          ← dynamic, always-current command list
```

## Command overview (prefix `!` and slash `/` both work)

- **Setup & admin** — `!csetup`, `!settings`, `!channelsetup`, `!rolesetup`,
  `!timingsetup`, `!limitssetup`, `!ows` (owner toggles), `!sync`, `!tutorial`
- **Tickets** — `!panel`, `!multipanel`, `!dropdownpanel`, `!reactionpanel`,
  `!new`, `!claim`, `!close`, `!transcript`, `!automate`, `!slaconfig`,
  `!analytics`, `!csat`, `!staffstats`, `!canned`, `!kb`, `!flow`, …
  (`!tickethelp` lists everything ticket-related)
- **Verification** — `!vsetup`, `!verification setup|config|panel|status|reset|enable|disable`
- **Polls** — `!poll create <minutes> <question> | <opt1> | <opt2>`,
  `!poll quick <question>`, `!poll end|cancel|results|list`
- **Invites** — `!invites [user]`, `!invites leaderboard`, `!invites setup`,
  `!invites add|remove|reset|config|resync`
- **Leveling** — `!rank`, `!leaderboard`, `!level config|give|set|remove|reset|reward|ignore`
- **AutoMod** — `!automod add|list|remove|enable|disable|exempt|config|strikes|test|logs`
- **Moderation** — `!warn`, `!warnings`, `!clearwarnings`, `!purge`, `!kick`,
  `!ban`, `!banid`, `!softban`, `!mute`, `!tempmute`, `!lock`/`!unlock`,
  `!slowmode`, `!blacklist`, `!msglog`, `!stickyrole`, `!securitycheck`, …
- **Help** — `!help`, `!help <command>`, `!help <category>`

## Project Layout
```
PythonFiles/
  Bot.py                  # core bot: config, events, moderation, ticket core
  cogs/                   # the six subsystems + setup/help (loaded via extensions)
    botkit.py             # shared DB/embed/util helpers for the cogs
    verification.py       polls.py       invites.py
    leveling.py           automod.py     setup.py     help.py
  TicketTool/             # ticket feature package (26 modules)
  ReactionRoles/          # reaction roles package (5 modules)
data/bot_data.db          # SQLite (auto-created + migrated)
Bat Files/                # Windows / unix launchers
```

## Notes
- Slash commands for the premium ticket features are guild-scoped to the
  configured home guilds (Discord's 100-global-command limit). Set
  `HOME_GUILD_IDS` in `.env`; prefix (`!`) commands work everywhere.
- Requires the **Manage Channels** permission for most ticket staff commands
  (see `!permissionlevel` for the ticket access model).
- Everything runs from one process — the legacy multi-bot launcher was
  removed; FactionBot is a single focused bot.
