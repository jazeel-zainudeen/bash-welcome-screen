# 🚀 Terminal Suite: `welcome` & `sshm` (`bash-welcome-screen`)

A fast, lightweight, and modern Linux terminal productivity suite featuring a gorgeous interactive startup welcome dashboard (`welcome`) and an interactive TUI SSH connection manager (`sshm`).

Built with pure Python 3 and **zero external dependencies**.

```text
╭──────────────────────────────────────────────────────────────────────────────╮
│ ✨ Welcome back, User!                        🐧 Ubuntu 22.04.2 LTS (x86_64) │
│ 📅 Tue, Sep 08 2026 · 08:00:00 PM                      ⏱️  Uptime: 12d 7h 00m │
├──────────────────────────────────────┬───────────────────────────────────────┤
│ SYSTEM & HARDWARE                    │ RESOURCE USAGE                        │
│ OS     : Ubuntu 22.04.2 LTS          │ CPU  [■■■░░░░░] 36.1% 37.0°C          │
│ Kernel : 6.8.0-124-generic           │ RAM  [■■■■■■░░] 6.1/7.6GB (80%)       │
│ CPU    : Intel Core i5-10400 (12T)   │ Disk [■■■■░░░░] 110/219GB (50%)       │
│ Host   : user@desktop                │ Swap [■■■░░░░░] 3.9/12.0GB (33%)      │
│ IP     : 192.168.1.100               │ Load : 1.99, 1.39, 0.90 (1, 5, 15m)   │
├──────────────────────────────────────────────────────────────────────────────┤
│ 🌐 Host Overrides : 1 active, 3 disabled configured in /etc/hosts            │
│   ● 192.168.1.50    ➜ dev.local                                              │
│   ○ 192.168.1.55    ➜ staging.local (disabled)                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ 🔑 SSH Hosts     : 11 configured hosts in ~/.ssh/config                      │
│ ▸ sshm              Interactive SSH manager & connection picker              │
│ ▸ sshm <name>       Instant direct connect or filtered picker                │
│ ▸ welcome --hosts   View all host overrides (or -p to ping check)            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## ✨ Features

### 🖥️ Welcome Dashboard (`welcome`)
- ⚡ **Zero External Dependencies**: Pure Python 3 standard library (`os`, `sys`, `platform`, `subprocess`, etc.). No `pip install` or virtual environments needed.
- 📊 **Hardware & Resource Gauges**: Clean Unicode progress bars for CPU, RAM, Disk, Swap, CPU core count, load averages, and thermal sensors.
- 🎨 **Built-in Theme Engine**:
  - `tokyo-night` (Aurora / Tokyo Night - default)
  - `catppuccin` (Catppuccin Mocha)
  - `nord` (Nord Arctic)
  - `dracula` (Dracula Vampire)
  - `cyberpunk` (Cyberpunk Neon)
  - `monochrome` (Minimalist single-color)
- 🌐 **`/etc/hosts` Inspector & Toggle**: Automatically detects custom host overrides, provides reachability ping tests (`-p`), and allows toggling mappings (`-t`).
- 🌿 **Git Repository Context**: Automatically detects when you open a terminal in a Git repo, showing current branch and uncommitted file count.
- 🔑 **SSH Integration**: Summarizes configured hosts from `~/.ssh/config`.
- 📝 **Scratchpad Notes**: Simple built-in sticky notes / task list right on your welcome screen.
- ⏱️ **Multiple Modes**:
  - Full aesthetic box dashboard (default)
  - Compact single-line status bar (`--mini` / `-m`)
  - Live auto-refreshing monitor (`--watch` / `-w`)
  - Structured JSON export for scripting (`--json` / `-j`)

### 🔑 Interactive SSH Manager (`sshm`)
- 🚀 **Full TUI Host Picker**: Interactive terminal interface to browse and connect to hosts in `~/.ssh/config`.
- 🔍 **Fuzzy & Instant Search**: Filter instantly by alias, destination IP, user, or proxy.
- ⚡ **Direct Connect**: `sshm <query>` connects directly if there is a single match, or opens pre-filtered picker.
- 📡 **Latency & Health Probing**: Run live latency checks (`sshm test` or press `t`/`T` in the TUI).
- 🧙 **Add Host Wizard**: Interactive step-by-step wizard to append new hosts directly to `~/.ssh/config`.

---

## 📥 Installation

Clone the repository:

```bash
git clone https://github.com/jazeel-zainudeen/bash-welcome-screen.git
cd bash-welcome-screen
```

### Option A: Interactive Wizard (Recommended)

Run `./install.sh` without arguments in any terminal to launch the interactive setup wizard:

```bash
./install.sh
# or: ./install.sh -i
```

```text
╭──────────────────────────────────────────────────────────────────────────────╮
│   ✨ TERMINAL SUITE INSTALLER  •  welcome & sshm                             │
│   🐧 Ubuntu 22.04 LTS  🐍 Python 3.10  👤 User  🐚 bash                      │
├──────────────────────────────────────────────────────────────────────────────┤
│   ✔ Components  ❯  ✔ Profile  ❯  [3] Theme  ❯  4. Features  ❯  5. Confirm    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Choose a color theme for your terminal dashboard:                            │
│                                                                              │
│   ❯ [●] 1. Tokyo Night  ■ ■ ■ ■ ■         [○] 4. Dracula      ■ ■ ■ ■ ■      │
│     [○] 2. Catppuccin   ■ ■ ■ ■ ■         [○] 5. Cyberpunk    ■ ■ ■ ■ ■      │
│     [○] 3. Nord Arctic  ■ ■ ■ ■ ■         [○] 6. Monochrome   ■ ■ ■ ■ ■      │
├──────────────────────────────────────────────────────────────────────────────┤
│ LIVE PREVIEW: Tokyo Night (Aurora)                                           │
│  🌆 Good evening, User!                      🐧 Ubuntu 22.04 LTS (x86_64)    │
│  CPU  [■■■░░░░░] 36% 33°C             RAM  [■■■■■■░░] 6.1/7.6G (80%)         │
│  Disk [■■■■░░░░] 110/219GB (50%)      IP   192.168.1.100                     │
│  🌿 Git Context: bash-welcome-screen on  master (clean)                     │
├──────────────────────────────────────────────────────────────────────────────┤
│   [↑/↓] Select Theme  •  [1-6] Jump  •  [Enter] Next Step  •  [b] Back       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Interactive Wizard Highlights:**
- 🧭 **Multi-Step Guided Setup**: Select installation presets, customize individual aliases, personalize greeting display name, pick themes, and toggle dashboard widgets.
- 🎨 **Live Real-Time Theme Preview**: Color swatches and an instant mini dashboard preview reflecting the exact ANSI colors of the selected theme as you navigate.
- ⚡ **Animated Progress**: Live checkmarks and step validation during installation.
- 🚀 **Instant Launch**: One-touch post-install menu to immediately test-run the welcome screen or launch the SSH manager.

### Option B: Command-Line Flags & Automation

```bash
./install.sh --all                        # Install both welcome and sshm
./install.sh --welcome                    # Install only welcome dashboard
./install.sh --sshm                       # Install only sshm
./install.sh --name "Your Name"           # Set custom greeting display name
./install.sh --theme catppuccin           # Set preferred theme
./install.sh --all --non-interactive      # Unattended / CI install
```

The installer creates symlinks in `~/.local/bin/` so updates via `git pull` are instantly reflected.

---

## 🛠️ Usage & Commands

### Welcome Dashboard (`welcome`)

```bash
welcome                  # Display full welcome dashboard
welcome --mini           # Single-line compact status summary (aliases: -m, --compact)
welcome --watch          # Live auto-refresh monitor (aliases: -w)
welcome --watch 1        # Live monitor with custom 1s refresh interval
welcome --json           # Output complete stats in JSON format (aliases: -j)
```

#### Theme & Configuration

```bash
welcome --theme catppuccin   # Temporarily view with a specific theme
welcome --config             # Show current config path and settings
```

To permanently customize settings, edit `~/.config/welcome/config.json`:

```json
{
  "user_name": "Your Name",
  "theme": "tokyo-night",
  "show_temperature": true,
  "show_hosts": true,
  "show_ssh": true,
  "show_git": true,
  "show_notes": true,
  "show_services_alert": true,
  "max_hosts_preview": 4,
  "max_notes_preview": 3
}
```

#### Host Overrides (`/etc/hosts`)

```bash
welcome --hosts          # List all custom /etc/hosts entries (active & disabled)
welcome --ping           # Ping test each custom host entry for connectivity
welcome --toggle <domain># Toggle domain active/disabled in /etc/hosts (requires sudo)
```

#### Quick Notes / Reminders

```bash
welcome --note "Deploy nginx update"   # Add task to ~/.welcome_notes
welcome --clear-notes                  # Clear all notes
```

---

### SSH Connection Manager (`sshm`)

```bash
sshm                     # Launch interactive TUI host manager & picker
sshm <query>             # Instant connect (if 1 match) or pre-filtered picker
sshm list, -l, ls        # Display formatted table of all SSH hosts
sshm test, -t [query]    # Test reachability and ping latency for hosts
sshm add, -a             # Launch interactive wizard to add a new host
sshm edit, -e            # Open ~/.ssh/config in your $EDITOR
```

#### TUI Keybindings

| Key | Action |
| --- | --- |
| `↑` / `↓`, `PgUp` / `PgDn` | Navigate server list |
| Letters / Numbers | Real-time search filter |
| `Backspace` / `Ctrl+U` | Delete last char / clear filter |
| `Enter` | Connect to selected host via SSH |
| `t` / `T` | Test latency of selected host / all hosts |
| `a` | Add new host wizard |
| `e` | Open `~/.ssh/config` in `$EDITOR` |
| `r` | Reload SSH configuration |
| `q` / `Esc` | Exit picker |

---

## 🗑️ Uninstallation

To remove installed symlinks:

```bash
./uninstall.sh           # Interactive selection
./uninstall.sh --all     # Remove all installed tools
./uninstall.sh --welcome # Remove only welcome
./uninstall.sh --sshm    # Remove only sshm
```

---

## 📂 Repository Structure

```text
bash-welcome-screen/
├── bin/                          # Executable Python tools
│   ├── welcome                   # Welcome dashboard MOTD
│   └── sshm                      # Interactive SSH manager
├── config/                       # Configuration templates
│   └── config.example.json       # Example configuration file
├── .editorconfig                 # Coding style definitions
├── install.sh                    # Modular interactive & CLI installer
├── uninstall.sh                  # Clean modular uninstaller
├── Makefile                      # Standard build/install/test targets
├── LICENSE                       # MIT License
└── README.md                     # Documentation
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
