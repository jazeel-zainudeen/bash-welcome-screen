# 🚀 Terminal Welcome Dashboard (`welcome`)

A fast, lightweight, and modern terminal dashboard designed for interactive shell startup (MOTD). Built with pure Python 3 and **zero external dependencies**.

```text
╭──────────────────────────────────────────────────────────────────────────────╮
│ ✨ Welcome back, User!                        🐧 Ubuntu 22.04.2 LTS (x86_64) │
│ 📅 Tue, Sep 08 2026 · 07:50:00 PM                      ⏱️  Uptime: 12d 6h 50m │
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
│ ▸ welcome --hosts   View all host overrides (or -p to ping check)            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## ✨ Features

- ⚡ **Zero External Dependencies**: Pure Python 3 standard library (`os`, `sys`, `platform`, `subprocess`, etc.). No `pip install` or virtualenv required.
- 📊 **Hardware & Resource Gauges**: Clean Unicode progress bars for CPU, RAM, Disk, Swap, plus CPU core count, load averages, and thermal sensors.
- 🎨 **Built-in Theme Engine**: Switch between stylish color palettes:
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

---

## 📥 Installation

### Quick Install (Automated)

Clone the repository and run the installer:

```bash
git clone https://github.com/jazeel-zainudeen/welcome-screen.git
cd welcome-screen
./install.sh
```

The installer will:
1. Symlink `welcome` (and aliases `motd`, `sysinfo`, `welcome-screen`) into `~/.local/bin/`.
2. Generate default configuration in `~/.config/welcome/config.json`.
3. Optionally prompt to add an interactive shell hook to your `~/.bashrc` or `~/.zshrc`.

---

### Manual Install

1. Make the script executable:
   ```bash
   chmod +x welcome
   ```
2. Symlink it to your local bin directory:
   ```bash
   mkdir -p ~/.local/bin
   ln -sf "$(pwd)/welcome" ~/.local/bin/welcome
   ```
3. Ensure `~/.local/bin` is in your `PATH` (add to `~/.bashrc` or `~/.zshrc` if needed):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
4. (Optional) Run automatically on interactive terminal launch:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc:
   if [[ $- == *i* ]] && [ -x "$HOME/.local/bin/welcome" ]; then
       "$HOME/.local/bin/welcome"
   fi
   ```

---

## 🛠️ Usage & Commands

```bash
welcome                  # Display full welcome dashboard
welcome --mini           # Single-line compact status summary (aliases: -m, --compact)
welcome --watch          # Live auto-refresh monitor (aliases: -w)
welcome --watch 1        # Live monitor with custom 1s refresh interval
welcome --json           # Output complete stats in JSON format (aliases: -j)
```

### Theme & Configuration

```bash
welcome --theme catppuccin   # Temporarily view with a specific theme
welcome --config             # Show current config path and settings
```

To permanently set a theme or customize dashboard widgets, edit `~/.config/welcome/config.json`:

```json
{
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

### Host Overrides (`/etc/hosts`)

```bash
welcome --hosts          # List all custom /etc/hosts entries (active & disabled)
welcome --ping           # Ping test each custom host entry for connectivity
welcome --toggle <domain># Toggle domain active/disabled in /etc/hosts (requires sudo)
```

### Built-in Quick Notes / Todo

```bash
welcome --note "Deploy nginx config update"   # Add task to ~/.welcome_notes
welcome --clear-notes                          # Clear all notes
```

---

## 🗑️ Uninstallation

To remove binary symlinks and clean up shell configurations:

```bash
./uninstall.sh
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
