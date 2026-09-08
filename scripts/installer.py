#!/usr/bin/env python3
"""
Terminal Welcome Dashboard & SSH Manager - Interactive Installer
Modern, interactive TUI wizard for installing 'welcome' and 'sshm'.
Features unified single-card UI, arrow key navigation, live theme swatches,
two-column layout, responsive box borders, and post-install launch options.
"""

import sys
import os
import time
import json
import shutil
import unicodedata
import re
import signal
import subprocess
import pwd
import select
from typing import Dict, List, Any, Optional

# Base Paths
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(REPO_DIR, 'bin')
CONFIG_DIR = os.path.join(REPO_DIR, 'config')
TARGET_DIR = os.path.expanduser('~/.local/bin')
USER_CONFIG_DIR = os.path.expanduser('~/.config/welcome')
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, 'config.json')

# --- Theme Definitions ---
THEMES = {
    'tokyo-night': {
        'name': 'Tokyo Night (Aurora)',
        'c_cyan': '\033[38;5;117m',
        'c_cyan_b': '\033[38;5;51m',
        'c_indigo': '\033[38;5;141m',
        'c_indigo_b': '\033[38;5;147m',
        'c_emerald': '\033[38;5;49m',
        'c_amber': '\033[38;5;221m',
        'c_rose': '\033[38;5;203m',
        'c_slate': '\033[38;5;240m',
        'c_slate_l': '\033[38;5;246m',
        'c_white': '\033[38;5;255m',
        'c_gray_bg': '\033[38;5;238m',
    },
    'catppuccin': {
        'name': 'Catppuccin Mocha',
        'c_cyan': '\033[38;5;117m',
        'c_cyan_b': '\033[38;5;111m',
        'c_indigo': '\033[38;5;183m',
        'c_indigo_b': '\033[38;5;147m',
        'c_emerald': '\033[38;5;150m',
        'c_amber': '\033[38;5;216m',
        'c_rose': '\033[38;5;210m',
        'c_slate': '\033[38;5;239m',
        'c_slate_l': '\033[38;5;248m',
        'c_white': '\033[38;5;254m',
        'c_gray_bg': '\033[38;5;237m',
    },
    'nord': {
        'name': 'Nord Arctic',
        'c_cyan': '\033[38;5;110m',
        'c_cyan_b': '\033[38;5;117m',
        'c_indigo': '\033[38;5;68m',
        'c_indigo_b': '\033[38;5;111m',
        'c_emerald': '\033[38;5;151m',
        'c_amber': '\033[38;5;222m',
        'c_rose': '\033[38;5;167m',
        'c_slate': '\033[38;5;238m',
        'c_slate_l': '\033[38;5;245m',
        'c_white': '\033[38;5;253m',
        'c_gray_bg': '\033[38;5;236m',
    },
    'dracula': {
        'name': 'Dracula Vampire',
        'c_cyan': '\033[38;5;159m',
        'c_cyan_b': '\033[38;5;86m',
        'c_indigo': '\033[38;5;141m',
        'c_indigo_b': '\033[38;5;183m',
        'c_emerald': '\033[38;5;120m',
        'c_amber': '\033[38;5;215m',
        'c_rose': '\033[38;5;212m',
        'c_slate': '\033[38;5;239m',
        'c_slate_l': '\033[38;5;247m',
        'c_white': '\033[38;5;255m',
        'c_gray_bg': '\033[38;5;237m',
    },
    'cyberpunk': {
        'name': 'Cyberpunk Neon',
        'c_cyan': '\033[38;5;51m',
        'c_cyan_b': '\033[38;5;45m',
        'c_indigo': '\033[38;5;198m',
        'c_indigo_b': '\033[38;5;201m',
        'c_emerald': '\033[38;5;46m',
        'c_amber': '\033[38;5;226m',
        'c_rose': '\033[38;5;196m',
        'c_slate': '\033[38;5;241m',
        'c_slate_l': '\033[38;5;249m',
        'c_white': '\033[38;5;231m',
        'c_gray_bg': '\033[38;5;238m',
    },
    'monochrome': {
        'name': 'Monochrome Minimal',
        'c_cyan': '\033[38;5;252m',
        'c_cyan_b': '\033[38;5;255m',
        'c_indigo': '\033[38;5;250m',
        'c_indigo_b': '\033[38;5;253m',
        'c_emerald': '\033[38;5;255m',
        'c_amber': '\033[38;5;251m',
        'c_rose': '\033[38;5;245m',
        'c_slate': '\033[38;5;240m',
        'c_slate_l': '\033[38;5;245m',
        'c_white': '\033[38;5;255m',
        'c_gray_bg': '\033[38;5;236m',
    }
}

# --- ANSI Formatting Constants ---
C_RESET    = '\033[0m'
C_BOLD     = '\033[1m'
C_DIM      = '\033[2m'
C_ITALIC   = '\033[3m'
C_UNDER    = '\033[4m'

# Default Palette
C_CYAN     = '\033[38;5;117m'
C_CYAN_B   = '\033[38;5;51m'
C_INDIGO   = '\033[38;5;141m'
C_INDIGO_B = '\033[38;5;147m'
C_EMERALD  = '\033[38;5;49m'
C_AMBER    = '\033[38;5;221m'
C_ROSE     = '\033[38;5;203m'
C_SLATE    = '\033[38;5;240m'
C_SLATE_L  = '\033[38;5;246m'
C_WHITE    = '\033[38;5;255m'
C_GRAY_BG  = '\033[38;5;238m'

ANSI_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub('', s)

def char_width(c: str) -> int:
    """Accurately calculates visual cell width for Unicode characters and emojis."""
    if not c:
        return 0
    if len(c) > 1:
        return sum(char_width(ch) for ch in c)
    if unicodedata.category(c) in ('Mn', 'Me', 'Cc', 'Cf'):
        return 0
    if unicodedata.east_asian_width(c) in ('F', 'W'):
        return 2
    code = ord(c)
    if (0x1F300 <= code <= 0x1FAFF) or code in (
        0x2728, 0x2705, 0x274C, 0x26A1, 0x2600, 0x2601, 0x2614, 0x2615, 0x26BD, 0x26BE,
        0x26C4, 0x26C5, 0x26CF, 0x26D4, 0x26EA, 0x26F2, 0x26F3, 0x26F5, 0x26FA, 0x26FD,
        0x23F1, 0x23F2, 0x23F3, 0x231A, 0x231B, 0x2702, 0x2709, 0x270A, 0x270B, 0x270C
    ):
        return 2
    return 1

def str_width(s: str) -> int:
    clean = strip_ansi(s)
    return sum(char_width(c) for c in clean)

def pad_to_width(s: str, width: int, align: str = 'left') -> str:
    w = str_width(s)
    pad = max(0, width - w)
    if align == 'left':
        return s + (' ' * pad)
    elif align == 'right':
        return (' ' * pad) + s
    else:
        pad_l = pad // 2
        pad_r = pad - pad_l
        return (' ' * pad_l) + s + (' ' * pad_r)

def clip_ansi_to_width(s: str, max_w: int) -> str:
    if str_width(s) <= max_w:
        return s
    res = []
    curr_w = 0
    i = 0
    n = len(s)
    while i < n:
        if s[i] == '\x1b':
            m = ANSI_RE.match(s, i)
            if m:
                res.append(m.group(0))
                i = m.end()
                continue
        cw = char_width(s[i])
        if curr_w + cw > max_w:
            break
        res.append(s[i])
        curr_w += cw
        i += 1
    res.append(C_RESET)
    return ''.join(res)

def get_system_environment() -> Dict[str, str]:
    distro = "Linux"
    if os.path.exists('/etc/os-release'):
        try:
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        distro = line.split('=', 1)[1].strip().strip('"\'')
                        break
        except Exception:
            pass

    try:
        pw = pwd.getpwuid(os.getuid())
        gecos = pw.pw_gecos.split(',')[0].strip()
        user_name = gecos or pw.pw_name.capitalize()
    except Exception:
        user_name = os.getenv('USER') or os.getenv('LOGNAME') or 'User'

    raw_shell = os.getenv('SHELL', '/bin/bash')
    shell_name = os.path.basename(raw_shell)
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    return {
        'distro': distro,
        'user_name': user_name,
        'shell': shell_name,
        'shell_path': raw_shell,
        'py_ver': py_ver
    }

def get_dynamic_greeting(name: str) -> str:
    now = time.localtime()
    hour = now.tm_hour
    if 5 <= hour < 12:
        return f"🌅 Good morning, {name}!"
    elif 12 <= hour < 18:
        return f"☀️  Good afternoon, {name}!"
    else:
        return f"🌆 Good evening, {name}!"

# --- Key Reading (Raw Terminal Mode) ---

def get_keypress(fd: int) -> str:
    ch = os.read(fd, 1).decode('latin1', errors='ignore')
    if not ch:
        return ''

    if ch == '\x1b':
        r, _, _ = select.select([fd], [], [], 0.04)
        if not r:
            return 'ESC'
        seq = '\x1b'
        while True:
            r, _, _ = select.select([fd], [], [], 0.01)
            if not r:
                break
            nxt = os.read(fd, 1).decode('latin1', errors='ignore')
            if not nxt:
                break
            seq += nxt
            if seq.endswith('~') or (len(seq) >= 3 and seq[1] in ('[', 'O') and seq[-1].isalpha()):
                break

        if seq in ('\x1b[A', '\x1bOA'): return 'UP'
        if seq in ('\x1b[B', '\x1bOB'): return 'DOWN'
        if seq in ('\x1b[C', '\x1bOC'): return 'RIGHT'
        if seq in ('\x1b[D', '\x1bOD'): return 'LEFT'
        if seq in ('\x1b[H', '\x1b[1~', '\x1bOH'): return 'HOME'
        if seq in ('\x1b[F', '\x1b[4~', '\x1bOF'): return 'END'
        if seq == '\x1b[5~': return 'PAGEUP'
        if seq == '\x1b[6~': return 'PAGEDOWN'
        if seq == '\x1b[3~': return 'DELETE'
        return 'ESC'

    if ch in ('\r', '\n'): return 'ENTER'
    if ch in ('\x7f', '\x08'): return 'BACKSPACE'
    if ch == ' ': return 'SPACE'
    if ch == '\x15': return 'CTRL_U'
    if ch == '\x03': return 'CTRL_C'
    if ch == '\x04': return 'CTRL_D'
    if ch == '\t': return 'TAB'
    return ch

# --- Unified Box Formatter ---

class UnifiedDashboardCard:
    """
    Renders a unified, seamlessly framed dashboard card with dividers and 
    exact character width calculation on every row.
    """
    def __init__(self, target_width: int = 78):
        term_cols = shutil.get_terminal_size((80, 24)).columns
        self.width = min(target_width, max(40, term_cols - 2))
        self.inner_width = self.width - 2
        self.border_c = C_SLATE

    def top(self) -> str:
        return f"{self.border_c}╭" + ("─" * self.width) + f"╮{C_RESET}"

    def mid(self) -> str:
        return f"{self.border_c}├" + ("─" * self.width) + f"┤{C_RESET}"

    def bottom(self) -> str:
        return f"{self.border_c}╰" + ("─" * self.width) + f"╯{C_RESET}"

    def row(self, content: str = "") -> str:
        clipped = clip_ansi_to_width(content, self.inner_width)
        padded = pad_to_width(clipped, self.inner_width)
        return f"{self.border_c}│{C_RESET} {padded} {self.border_c}│{C_RESET}"

    def split_row(self, left: str, right: str) -> str:
        half_w = self.inner_width // 2
        l_pad = pad_to_width(clip_ansi_to_width(left, half_w), half_w)
        r_pad = pad_to_width(clip_ansi_to_width(right, self.inner_width - half_w), self.inner_width - half_w)
        return f"{self.border_c}│{C_RESET} {l_pad}{r_pad} {self.border_c}│{C_RESET}"

# --- Interactive TUI Wizard Application ---

class InstallerWizard:
    def __init__(self, cli_args: Dict[str, Any]):
        self.cli_args = cli_args
        self.sys_env = get_system_environment()

        # Wizard State
        self.step_idx = 0
        self.running = True

        # Step 0: Component Presets
        self.component_preset_idx = 0
        self.component_options = [
            ("Full Suite (Recommended)", "Welcome Dashboard MOTD + Interactive SSH Manager (sshm)"),
            ("Welcome Dashboard Only", "System gauges, Git context, host overrides, thermal stats & notes"),
            ("SSH Connection Manager Only", "Interactive TUI SSH connection picker, latency tester, host wizard"),
            ("Custom Component Selection", "Fine-grained selection of individual executables and symlinks")
        ]

        self.custom_binaries = [
            {'key': 'welcome', 'name': 'welcome', 'desc': 'Main Welcome Dashboard MOTD executable', 'enabled': True},
            {'key': 'motd', 'name': 'motd', 'desc': 'Symlink alias for welcome', 'enabled': True},
            {'key': 'sysinfo', 'name': 'sysinfo', 'desc': 'System hardware status alias', 'enabled': True},
            {'key': 'welcome-screen', 'name': 'welcome-screen', 'desc': 'Alternative command alias', 'enabled': True},
            {'key': 'sshm', 'name': 'sshm', 'desc': 'Interactive SSH Connection Manager TUI', 'enabled': True},
            {'key': 'sshc', 'name': 'sshc', 'desc': 'SSH fast-connect shortcut alias', 'enabled': True},
            {'key': 'ssh-menu', 'name': 'ssh-menu', 'desc': 'SSH interactive menu alias', 'enabled': True},
        ]
        self.custom_cursor = 0

        # Step 1: User Profile / Greeting Name
        self.greeting_name = self.cli_args.get('name') or self.sys_env['user_name']

        # Step 2: Theme Selection
        self.theme_keys = list(THEMES.keys())
        default_theme = self.cli_args.get('theme', 'tokyo-night')
        self.selected_theme_idx = self.theme_keys.index(default_theme) if default_theme in self.theme_keys else 0

        # Step 3: Shell Hooks & Feature Toggles
        detected_rcs = []
        for rc in [os.path.expanduser('~/.bashrc'), os.path.expanduser('~/.zshrc')]:
            if os.path.exists(rc):
                detected_rcs.append(rc)
        if not detected_rcs and os.path.exists(os.path.expanduser('~/.profile')):
            detected_rcs.append(os.path.expanduser('~/.profile'))

        self.feature_items = []
        for rc in detected_rcs:
            rc_name = os.path.basename(rc)
            self.feature_items.append({
                'type': 'hook',
                'path': rc,
                'label': f'Auto-run welcome dashboard on interactive launch ({rc_name})',
                'enabled': True
            })

        self.feature_items.extend([
            {'type': 'config', 'key': 'show_temperature', 'label': 'Hardware temperature monitoring', 'enabled': True},
            {'type': 'config', 'key': 'show_git', 'label': 'Git repository context (branch & clean/dirty state)', 'enabled': True},
            {'type': 'config', 'key': 'show_hosts', 'label': 'Custom /etc/hosts domain overrides preview', 'enabled': True},
            {'type': 'config', 'key': 'show_ssh', 'label': 'SSH configured hosts counter (~/.ssh/config)', 'enabled': True},
            {'type': 'config', 'key': 'show_notes', 'label': 'Scratchpad notes reminder widget (~/.welcome_notes)', 'enabled': True},
            {'type': 'config', 'key': 'show_services_alert', 'label': 'Failed systemd unit alerts', 'enabled': True},
        ])
        self.feature_cursor = 0
        self.post_install_cursor = 0

    def active_steps(self) -> List[str]:
        install_welcome = self.wants_welcome()
        steps = ["Components"]
        if self.component_preset_idx == 3:
            steps.append("Customize")
        if install_welcome:
            steps.append("Profile")
            steps.append("Theme")
            steps.append("Features")
        steps.append("Confirm")
        return steps

    def wants_welcome(self) -> bool:
        if self.component_preset_idx in (0, 1):
            return True
        if self.component_preset_idx == 2:
            return False
        return any(b['enabled'] for b in self.custom_binaries if b['key'] in ('welcome', 'motd', 'sysinfo', 'welcome-screen'))

    def wants_sshm(self) -> bool:
        if self.component_preset_idx in (0, 2):
            return True
        if self.component_preset_idx == 1:
            return False
        return any(b['enabled'] for b in self.custom_binaries if b['key'] in ('sshm', 'sshc', 'ssh-menu'))

    def render_header(self, card: UnifiedDashboardCard, lines: List[str]):
        lines.append(card.top())
        banner_title = f"  ✨ {C_BOLD}{C_CYAN_B}TERMINAL SUITE INSTALLER{C_RESET}  {C_SLATE}•{C_RESET}  {C_WHITE}welcome & sshm{C_RESET}"
        lines.append(card.row(banner_title))

        badges = (
            f"  {C_INDIGO}🐧 {self.sys_env['distro'][:22]}{C_RESET}  "
            f"{C_CYAN}🐍 Python {self.sys_env['py_ver']}{C_RESET}  "
            f"{C_EMERALD}👤 {self.sys_env['user_name']}{C_RESET}  "
            f"{C_AMBER}🐚 {self.sys_env['shell']}{C_RESET}"
        )
        lines.append(card.row(badges))
        lines.append(card.mid())

        # Step Indicator Breadcrumbs
        steps = self.active_steps()
        crumb_parts = []
        for idx, s in enumerate(steps):
            if idx == self.step_idx:
                crumb_parts.append(f"{C_BOLD}{C_CYAN_B}[{idx+1}] {s}{C_RESET}")
            elif idx < self.step_idx:
                crumb_parts.append(f"{C_EMERALD}✔ {s}{C_RESET}")
            else:
                crumb_parts.append(f"{C_SLATE_L}{idx+1}. {s}{C_RESET}")
        lines.append(card.row(f"  {'  ❯  '.join(crumb_parts)}"))
        lines.append(card.mid())

    def draw(self):
        card = UnifiedDashboardCard(78)
        buffer = []
        self.render_header(card, buffer)

        steps = self.active_steps()
        current_step_name = steps[self.step_idx]

        if current_step_name == "Components":
            self.draw_step_components(card, buffer)
        elif current_step_name == "Customize":
            self.draw_step_custom_components(card, buffer)
        elif current_step_name == "Profile":
            self.draw_step_profile(card, buffer)
        elif current_step_name == "Theme":
            self.draw_step_theme(card, buffer)
        elif current_step_name == "Features":
            self.draw_step_features(card, buffer)
        elif current_step_name == "Confirm":
            self.draw_step_confirm(card, buffer)

        # Draw frame into terminal screen buffer
        out = "\033[H" + "\r\n".join(buffer) + "\033[J"
        sys.stdout.write(out)
        sys.stdout.flush()

    def draw_step_components(self, card: UnifiedDashboardCard, buffer: List[str]):
        buffer.append(card.row(f"{C_WHITE}Choose components to install:{C_RESET}"))
        buffer.append(card.row(""))

        for i, (name, desc) in enumerate(self.component_options):
            is_active = (i == self.component_preset_idx)
            cursor = f"{C_CYAN_B}❯{C_RESET}" if is_active else " "
            bullet = f"{C_EMERALD}●{C_RESET}" if is_active else f"{C_SLATE}○{C_RESET}"
            title_styled = f"{C_BOLD}{C_WHITE}{name}{C_RESET}" if is_active else f"{C_WHITE}{name}{C_RESET}"

            buffer.append(card.row(f"  {cursor} [{bullet}] {C_AMBER}{i+1}.{C_RESET} {title_styled}"))
            buffer.append(card.row(f"        {C_SLATE_L}{desc}{C_RESET}"))
            if i < len(self.component_options) - 1:
                buffer.append(card.row(""))

        buffer.append(card.mid())
        buffer.append(card.row(f"  {C_SLATE_L}[↑/↓] Navigate  •  [1-4] Quick Select  •  {C_CYAN}[Enter] Next Step{C_RESET}  •  [q] Quit"))
        buffer.append(card.bottom())

    def draw_step_custom_components(self, card: UnifiedDashboardCard, buffer: List[str]):
        buffer.append(card.row(f"{C_WHITE}Toggle individual tools and aliases to install with {C_CYAN}[Space]{C_WHITE}:{C_RESET}"))
        buffer.append(card.row(""))

        for i, item in enumerate(self.custom_binaries):
            is_cursor = (i == self.custom_cursor)
            ptr = f"{C_CYAN_B}❯{C_RESET}" if is_cursor else " "
            chk = f"{C_EMERALD}✔{C_RESET}" if item['enabled'] else " "
            name_c = f"{C_BOLD}{C_WHITE}" if is_cursor else C_WHITE
            buffer.append(card.row(f"  {ptr} [{chk}] {name_c}{item['name']:<16}{C_RESET} {C_SLATE_L}{item['desc']}{C_RESET}"))

        buffer.append(card.row(""))
        buffer.append(card.row(f"  {C_SLATE_L}Tip: Press 'a' to toggle all on/off.{C_RESET}"))
        buffer.append(card.mid())
        buffer.append(card.row(f"  {C_SLATE_L}[↑/↓] Move  •  [Space] Toggle  •  [a] All  •  {C_CYAN}[Enter] Next{C_RESET}  •  [b] Back"))
        buffer.append(card.bottom())

    def draw_step_profile(self, card: UnifiedDashboardCard, buffer: List[str]):
        greeting_preview = get_dynamic_greeting(self.greeting_name or "User")
        buffer.append(card.row(f"{C_WHITE}Personalize your greeting on terminal startup:{C_RESET}"))
        buffer.append(card.row(""))
        buffer.append(card.row(f"  {C_SLATE_L}Live Greeting Preview:{C_RESET}"))
        buffer.append(card.row(f"    {C_BOLD}{C_CYAN_B}{greeting_preview}{C_RESET}"))
        buffer.append(card.row(""))
        buffer.append(card.row(f"  {C_WHITE}Preferred Display Name:{C_RESET}"))
        buffer.append(card.row(f"    {C_AMBER}▸{C_RESET} {C_BOLD}{C_WHITE}{self.greeting_name}{C_RESET}{C_CYAN_B}█{C_RESET}"))
        buffer.append(card.row(""))
        buffer.append(card.row(f"  {C_SLATE_L}Tip: You can change this later anytime in ~/.config/welcome/config.json{C_RESET}"))
        buffer.append(card.mid())
        buffer.append(card.row(f"  {C_SLATE_L}[Type] Edit Name  •  [Bksp] Delete  •  {C_CYAN}[Enter] Next{C_RESET}  •  [Esc] Back"))
        buffer.append(card.bottom())

    def draw_step_theme(self, card: UnifiedDashboardCard, buffer: List[str]):
        buffer.append(card.row(f"{C_WHITE}Choose a color theme for your terminal dashboard:{C_RESET}"))
        buffer.append(card.row(""))

        # Render 6 themes in 2 clean side-by-side columns (3 rows)
        short_names = {
            'tokyo-night': 'Tokyo Night',
            'catppuccin': 'Catppuccin',
            'nord': 'Nord Arctic',
            'dracula': 'Dracula',
            'cyberpunk': 'Cyberpunk',
            'monochrome': 'Monochrome'
        }

        col_w = card.inner_width // 2
        for r in range(3):
            idx1 = r
            idx2 = r + 3
            k1 = self.theme_keys[idx1]
            k2 = self.theme_keys[idx2]
            t1 = THEMES[k1]
            t2 = THEMES[k2]

            is_sel1 = (idx1 == self.selected_theme_idx)
            is_sel2 = (idx2 == self.selected_theme_idx)

            cur1 = f"{C_CYAN_B}❯{C_RESET}" if is_sel1 else " "
            bul1 = f"{C_EMERALD}●{C_RESET}" if is_sel1 else f"{C_SLATE}○{C_RESET}"
            name1 = f"{C_BOLD}{C_WHITE}{short_names[k1]:<12}{C_RESET}" if is_sel1 else f"{C_WHITE}{short_names[k1]:<12}{C_RESET}"
            sw1 = f"{t1['c_cyan']}■{C_RESET} {t1['c_indigo']}■{C_RESET} {t1['c_emerald']}■{C_RESET} {t1['c_amber']}■{C_RESET} {t1['c_rose']}■{C_RESET}"
            col1 = f"  {cur1} [{bul1}] {C_AMBER}{idx1+1}.{C_RESET} {name1} {sw1}"

            cur2 = f"{C_CYAN_B}❯{C_RESET}" if is_sel2 else " "
            bul2 = f"{C_EMERALD}●{C_RESET}" if is_sel2 else f"{C_SLATE}○{C_RESET}"
            name2 = f"{C_BOLD}{C_WHITE}{short_names[k2]:<12}{C_RESET}" if is_sel2 else f"{C_WHITE}{short_names[k2]:<12}{C_RESET}"
            sw2 = f"{t2['c_cyan']}■{C_RESET} {t2['c_indigo']}■{C_RESET} {t2['c_emerald']}■{C_RESET} {t2['c_amber']}■{C_RESET} {t2['c_rose']}■{C_RESET}"
            col2 = f"  {cur2} [{bul2}] {C_AMBER}{idx2+1}.{C_RESET} {name2} {sw2}"

            buffer.append(card.split_row(col1, col2))

        buffer.append(card.mid())

        # Integrated Live Theme Preview (Tokyo Night, etc.)
        curr_t = THEMES[self.theme_keys[self.selected_theme_idx]]
        tc_cyan_b = curr_t['c_cyan_b']
        tc_indigo = curr_t['c_indigo']
        tc_emerald = curr_t['c_emerald']
        tc_amber = curr_t['c_amber']
        tc_white = curr_t['c_white']
        tc_slate_l = curr_t['c_slate_l']

        preview_greeting = get_dynamic_greeting(self.greeting_name or "User")
        buffer.append(card.row(f"{C_BOLD}{tc_cyan_b}LIVE PREVIEW: {curr_t['name']}{C_RESET}"))

        # Row 1: Greeting + Distro
        r1_l = f" {tc_cyan_b}{preview_greeting}{C_RESET}"
        r1_r = f"{tc_indigo}🐧 {self.sys_env['distro'][:20]} ({os.uname().machine}){C_RESET}"
        r1 = pad_to_width(r1_l, card.inner_width - str_width(r1_r)) + r1_r
        buffer.append(card.row(r1))

        # Row 2: CPU + RAM
        r2_l = f" {tc_slate_l}CPU  {tc_emerald}[■■■░░░░░] 36% 33°C{C_RESET}"
        r2_r = f"{tc_slate_l}RAM  {tc_indigo}[■■■■■■░░] 6.1/7.6G (80%){C_RESET}"
        buffer.append(card.split_row(r2_l, r2_r))

        # Row 3: Disk + IP
        r3_l = f" {tc_slate_l}Disk {tc_amber}[■■■■░░░░] 110/219GB (50%){C_RESET}"
        r3_r = f"{tc_slate_l}IP   {tc_white}172.17.4.74{C_RESET}"
        buffer.append(card.split_row(r3_l, r3_r))

        # Row 4: Git
        r4 = f" {tc_emerald}🌿 Git Context: bash-welcome-screen on  master (clean){C_RESET}"
        buffer.append(card.row(r4))

        buffer.append(card.mid())
        buffer.append(card.row(f"  {C_SLATE_L}[↑/↓] Select Theme  •  [1-6] Jump  •  {C_CYAN}[Enter] Next Step{C_RESET}  •  [b] Back"))
        buffer.append(card.bottom())

    def draw_step_features(self, card: UnifiedDashboardCard, buffer: List[str]):
        buffer.append(card.row(f"{C_WHITE}Configure automatic startup hooks and dashboard features:{C_RESET}"))
        buffer.append(card.row(""))

        has_hook_section = False
        has_widget_section = False

        for i, item in enumerate(self.feature_items):
            is_cursor = (i == self.feature_cursor)
            ptr = f"{C_CYAN_B}❯{C_RESET}" if is_cursor else " "
            chk = f"{C_EMERALD}✔{C_RESET}" if item['enabled'] else " "

            if item['type'] == 'hook' and not has_hook_section:
                buffer.append(card.row(f"  {C_BOLD}{C_CYAN}Shell Startup Hooks:{C_RESET}"))
                has_hook_section = True
            elif item['type'] == 'config' and not has_widget_section:
                buffer.append(card.row(""))
                buffer.append(card.row(f"  {C_BOLD}{C_CYAN}Dashboard Widgets:{C_RESET}"))
                has_widget_section = True

            lbl_styled = f"{C_BOLD}{C_WHITE}{item['label']}{C_RESET}" if is_cursor else f"{C_WHITE}{item['label']}{C_RESET}"
            buffer.append(card.row(f"  {ptr} [{chk}] {lbl_styled}"))

        buffer.append(card.mid())
        buffer.append(card.row(f"  {C_SLATE_L}[↑/↓] Navigate  •  [Space] Toggle  •  {C_CYAN}[Enter] Next Step{C_RESET}  •  [b] Back"))
        buffer.append(card.bottom())

    def draw_step_confirm(self, card: UnifiedDashboardCard, buffer: List[str]):
        install_welcome = self.wants_welcome()
        install_sshm = self.wants_sshm()

        comp_parts = []
        if install_welcome and install_sshm:
            comp_parts.append("Welcome Dashboard + SSH Connection Manager")
        elif install_welcome:
            comp_parts.append("Welcome Dashboard Only")
        elif install_sshm:
            comp_parts.append("SSH Connection Manager Only")
        else:
            comp_parts.append("Custom Component Selection")

        active_theme_name = THEMES[self.theme_keys[self.selected_theme_idx]]['name']

        active_hooks = [os.path.basename(f['path']) for f in self.feature_items if f['type'] == 'hook' and f['enabled']]
        hook_str = f"Auto-start in {', '.join(active_hooks)}" if active_hooks else "None (Manual invocation)"

        symlinks_to_create = []
        if self.component_preset_idx != 3:
            if install_welcome:
                symlinks_to_create.extend(['welcome', 'motd', 'sysinfo', 'welcome-screen'])
            if install_sshm:
                symlinks_to_create.extend(['sshm', 'sshc', 'ssh-menu'])
        else:
            symlinks_to_create = [b['name'] for b in self.custom_binaries if b['enabled']]

        buffer.append(card.row(f"{C_WHITE}Review your installation settings before applying:{C_RESET}"))
        buffer.append(card.row(""))
        buffer.append(card.row(f"  {C_CYAN}📦 Components   :{C_RESET} {C_BOLD}{C_WHITE}{', '.join(comp_parts)}{C_RESET}"))
        buffer.append(card.row(f"  {C_CYAN}📁 Target Path  :{C_RESET} {C_WHITE}{TARGET_DIR}{C_RESET}"))

        if install_welcome:
            buffer.append(card.row(f"  {C_CYAN}👤 Greeting     :{C_RESET} {C_WHITE}\"{self.greeting_name}\" ({get_dynamic_greeting(self.greeting_name)}){C_RESET}"))
            buffer.append(card.row(f"  {C_CYAN}🎨 Theme        :{C_RESET} {C_WHITE}{active_theme_name}{C_RESET}"))
            buffer.append(card.row(f"  {C_CYAN}⚙️  Config File  :{C_RESET} {C_WHITE}{USER_CONFIG_FILE}{C_RESET}"))
            buffer.append(card.row(f"  {C_CYAN}🐚 Startup Hooks:{C_RESET} {C_WHITE}{hook_str}{C_RESET}"))

        buffer.append(card.row(""))
        buffer.append(card.row(f"  {C_SLATE_L}Symlinks to be created: {C_EMERALD}{', '.join(symlinks_to_create)}{C_RESET}"))
        buffer.append(card.mid())
        buffer.append(card.row(f"  {C_EMERALD}{C_BOLD}[Enter] ⚡ Install Now{C_RESET}    {C_SLATE_L}[b] Back / Adjust    [q] Cancel{C_RESET}"))
        buffer.append(card.bottom())

    def run_animated_install(self):
        """Performs the actual installation with live animated steps in the unified card."""
        install_welcome = self.wants_welcome()
        install_sshm = self.wants_sshm()
        completed_lines = []

        def render_progress():
            card = UnifiedDashboardCard(78)
            buf = []
            self.render_header(card, buf)
            buf.append(card.row(f"{C_BOLD}{C_CYAN}Applying installation steps:{C_RESET}"))
            buf.append(card.row(""))
            for cl in completed_lines:
                buf.append(card.row(cl))
            buf.append(card.row(""))
            buf.append(card.row(f"{C_SLATE_L}Installing selected components...{C_RESET}"))
            buf.append(card.bottom())
            sys.stdout.write("\033[H" + "\r\n".join(buf) + "\033[J")
            sys.stdout.flush()

        # 1. Target Directory
        os.makedirs(TARGET_DIR, exist_ok=True)
        completed_lines.append(f"  {C_EMERALD}✔{C_RESET} Destination directory {TARGET_DIR} verified")
        render_progress()
        time.sleep(0.12)

        # 2. Welcome Binaries
        if install_welcome:
            welcome_src = os.path.join(BIN_DIR, 'welcome')
            os.chmod(welcome_src, 0o755)
            syms = ['welcome', 'motd', 'sysinfo', 'welcome-screen']
            if self.component_preset_idx == 3:
                syms = [b['name'] for b in self.custom_binaries if b['enabled'] and b['key'] in ('welcome', 'motd', 'sysinfo', 'welcome-screen')]
            for s in syms:
                dest = os.path.join(TARGET_DIR, s)
                if os.path.islink(dest) or os.path.exists(dest):
                    os.remove(dest)
                os.symlink(welcome_src, dest)
            completed_lines.append(f"  {C_EMERALD}✔{C_RESET} Linked Welcome Dashboard ({', '.join(syms)})")
            render_progress()
            time.sleep(0.12)

        # 3. SSHM Binaries
        if install_sshm:
            sshm_src = os.path.join(BIN_DIR, 'sshm')
            os.chmod(sshm_src, 0o755)
            syms = ['sshm', 'sshc', 'ssh-menu']
            if self.component_preset_idx == 3:
                syms = [b['name'] for b in self.custom_binaries if b['enabled'] and b['key'] in ('sshm', 'sshc', 'ssh-menu')]
            for s in syms:
                dest = os.path.join(TARGET_DIR, s)
                if os.path.islink(dest) or os.path.exists(dest):
                    os.remove(dest)
                os.symlink(sshm_src, dest)
            completed_lines.append(f"  {C_EMERALD}✔{C_RESET} Linked SSH Manager ({', '.join(syms)})")
            render_progress()
            time.sleep(0.12)

        # 4. Config file
        if install_welcome:
            os.makedirs(USER_CONFIG_DIR, exist_ok=True)
            cfg = {
                'user_name': self.greeting_name,
                'theme': self.theme_keys[self.selected_theme_idx],
                'max_hosts_preview': 4,
                'max_notes_preview': 3
            }
            for item in self.feature_items:
                if item['type'] == 'config':
                    cfg[item['key']] = item['enabled']

            with open(USER_CONFIG_FILE, 'w') as f:
                json.dump(cfg, f, indent=2)
            completed_lines.append(f"  {C_EMERALD}✔{C_RESET} Configuration written to {USER_CONFIG_FILE}")
            render_progress()
            time.sleep(0.12)

        # 5. Shell Hooks
        if install_welcome:
            hook_code = 'if [[ $- == *i* ]] && [ -x "$HOME/.local/bin/welcome" ]; then "$HOME/.local/bin/welcome"; fi'
            for item in self.feature_items:
                if item['type'] == 'hook' and item['enabled']:
                    rc_path = item['path']
                    try:
                        content = ""
                        if os.path.exists(rc_path):
                            with open(rc_path, 'r') as f:
                                content = f.read()
                        if "welcome" not in content:
                            with open(rc_path, 'a') as f:
                                f.write(f"\n# Terminal Welcome Dashboard\n{hook_code}\n")
                    except Exception:
                        pass
            completed_lines.append(f"  {C_EMERALD}✔{C_RESET} Shell startup hooks successfully configured")
            render_progress()
            time.sleep(0.12)

        # 6. PATH check
        path_env = os.getenv('PATH', '')
        in_path = TARGET_DIR in path_env.split(':')
        if in_path:
            completed_lines.append(f"  {C_EMERALD}✔{C_RESET} PATH verified: {TARGET_DIR} is already in PATH")
        else:
            completed_lines.append(f"  {C_AMBER}ℹ{C_RESET} Note: Add {TARGET_DIR} to your PATH")
        render_progress()

        time.sleep(0.3)
        self.run_completion_screen()

    def run_completion_screen(self):
        actions = [
            ("🚀 Test-run Welcome Dashboard now", "welcome"),
            ("🔑 Launch Interactive SSH Manager (sshm) now", "sshm"),
            ("📄 Inspect ~/.config/welcome/config.json", "cat"),
            ("🚪 Exit to terminal", "exit")
        ]

        if not self.wants_welcome():
            actions.pop(0)
        if not self.wants_sshm():
            actions = [a for a in actions if a[1] != 'sshm']

        fd = sys.stdin.fileno()
        while True:
            card = UnifiedDashboardCard(78)
            buf = []
            self.render_header(card, buf)

            buf.append(card.row(f"{C_BOLD}{C_EMERALD}🎉 Installation completed successfully!{C_RESET}"))
            buf.append(card.row(f"{C_SLATE_L}All chosen tools and configuration files are ready to use.{C_RESET}"))
            buf.append(card.row(""))
            buf.append(card.row(f"{C_WHITE}What would you like to do next?{C_RESET}"))
            buf.append(card.row(""))

            for i, (label, cmd) in enumerate(actions):
                is_sel = (i == self.post_install_cursor)
                cursor = f"{C_CYAN_B}❯{C_RESET}" if is_sel else " "
                bullet = f"{C_EMERALD}●{C_RESET}" if is_sel else f"{C_SLATE}○{C_RESET}"
                lbl_styled = f"{C_BOLD}{C_WHITE}{label}{C_RESET}" if is_sel else f"{C_WHITE}{label}{C_RESET}"
                buf.append(card.row(f"  {cursor} [{bullet}] {C_AMBER}{i+1}.{C_RESET} {lbl_styled}"))

            buf.append(card.row(""))
            buf.append(card.row(f"  {C_SLATE_L}Tip: Run 'welcome' or 'sshm' anytime in your terminal.{C_RESET}"))
            buf.append(card.mid())
            buf.append(card.row(f"  {C_SLATE_L}[↑/↓] Select  •  [1-{len(actions)}] Quick Select  •  {C_CYAN}[Enter] Execute Choice{C_RESET}"))
            buf.append(card.bottom())

            sys.stdout.write("\033[H" + "\r\n".join(buf) + "\033[J")
            sys.stdout.flush()

            k = get_keypress(fd)
            if k in ('UP', 'k'):
                self.post_install_cursor = (self.post_install_cursor - 1) % len(actions)
            elif k in ('DOWN', 'j'):
                self.post_install_cursor = (self.post_install_cursor + 1) % len(actions)
            elif k in ('1', '2', '3', '4'):
                num = int(k) - 1
                if 0 <= num < len(actions):
                    self.post_install_cursor = num
                    choice_cmd = actions[num][1]
                    self.handle_post_action(choice_cmd)
                    return
            elif k == 'ENTER':
                choice_cmd = actions[self.post_install_cursor][1]
                self.handle_post_action(choice_cmd)
                return
            elif k in ('ESC', 'q', 'CTRL_C'):
                sys.stdout.write("\r\n\033[0m")
                sys.stdout.flush()
                return

    def handle_post_action(self, cmd: str):
        # Restore main terminal buffer
        sys.stdout.write("\033[?1049l\033[?25h\033[0m")
        sys.stdout.flush()
        import termios
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.old_term)
        except Exception:
            pass

        if cmd == 'welcome':
            welcome_bin = os.path.join(TARGET_DIR, 'welcome')
            if os.path.exists(welcome_bin):
                os.execv(welcome_bin, [welcome_bin])
            else:
                fallback = os.path.join(BIN_DIR, 'welcome')
                os.execv(fallback, [fallback])
        elif cmd == 'sshm':
            sshm_bin = os.path.join(TARGET_DIR, 'sshm')
            if os.path.exists(sshm_bin):
                os.execv(sshm_bin, [sshm_bin])
            else:
                fallback = os.path.join(BIN_DIR, 'sshm')
                os.execv(fallback, [fallback])
        elif cmd == 'cat':
            if os.path.exists(USER_CONFIG_FILE):
                print(f"{C_BOLD}{C_CYAN}Configuration ({USER_CONFIG_FILE}):{C_RESET}\n")
                with open(USER_CONFIG_FILE) as f:
                    print(f.read())
            print(f"{C_EMERALD}✓ Setup finished.{C_RESET}")
        else:
            print(f"{C_EMERALD}✓ Setup finished! Welcome to your new terminal suite.{C_RESET}\n")

    def run(self):
        """Main TUI event loop."""
        import termios
        import tty

        fd = sys.stdin.fileno()
        self.old_term = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            # Enter alternate screen buffer & hide cursor
            sys.stdout.write("\033[?1049h\033[?25l\033[2J\033[H")
            sys.stdout.flush()

            while self.running:
                self.draw()
                k = get_keypress(fd)
                steps = self.active_steps()
                current_step_name = steps[self.step_idx]

                if k in ('CTRL_C', 'CTRL_D'):
                    self.running = False
                    break

                if k == 'q' and current_step_name == "Components":
                    self.running = False
                    break

                # Back navigation
                if current_step_name != "Profile":
                    if (k in ('b', 'B', 'LEFT', 'ESC')) and self.step_idx > 0:
                        self.step_idx -= 1
                        continue
                else:
                    if (k in ('ESC',)) and self.step_idx > 0:
                        self.step_idx -= 1
                        continue

                # Step-specific key handling
                if current_step_name == "Components":
                    if k in ('UP', 'k'):
                        self.component_preset_idx = (self.component_preset_idx - 1) % len(self.component_options)
                    elif k in ('DOWN', 'j'):
                        self.component_preset_idx = (self.component_preset_idx + 1) % len(self.component_options)
                    elif k in ('1', '2', '3', '4'):
                        self.component_preset_idx = int(k) - 1
                    elif k == 'ENTER':
                        self.step_idx += 1

                elif current_step_name == "Customize":
                    if k in ('UP', 'k'):
                        self.custom_cursor = (self.custom_cursor - 1) % len(self.custom_binaries)
                    elif k in ('DOWN', 'j'):
                        self.custom_cursor = (self.custom_cursor + 1) % len(self.custom_binaries)
                    elif k == 'SPACE':
                        self.custom_binaries[self.custom_cursor]['enabled'] = not self.custom_binaries[self.custom_cursor]['enabled']
                    elif k in ('a', 'A'):
                        any_on = any(b['enabled'] for b in self.custom_binaries)
                        for b in self.custom_binaries:
                            b['enabled'] = not any_on
                    elif k == 'ENTER':
                        self.step_idx += 1

                elif current_step_name == "Profile":
                    if k == 'ENTER':
                        if not self.greeting_name.strip():
                            self.greeting_name = self.sys_env['user_name']
                        self.step_idx += 1
                    elif k in ('BACKSPACE', 'DELETE'):
                        if self.greeting_name:
                            self.greeting_name = self.greeting_name[:-1]
                    elif k == 'CTRL_U':
                        self.greeting_name = ""
                    elif len(k) == 1 and k.isprintable() and k not in ('\r', '\n', '\t'):
                        if len(self.greeting_name) < 28:
                            self.greeting_name += k

                elif current_step_name == "Theme":
                    if k in ('UP', 'k'):
                        self.selected_theme_idx = (self.selected_theme_idx - 1) % len(self.theme_keys)
                    elif k in ('DOWN', 'j'):
                        self.selected_theme_idx = (self.selected_theme_idx + 1) % len(self.theme_keys)
                    elif k in ('LEFT', 'h'):
                        if self.selected_theme_idx >= 3:
                            self.selected_theme_idx -= 3
                    elif k in ('RIGHT', 'l'):
                        if self.selected_theme_idx < 3:
                            self.selected_theme_idx += 3
                    elif k in [str(x) for x in range(1, len(self.theme_keys) + 1)]:
                        self.selected_theme_idx = int(k) - 1
                    elif k == 'ENTER':
                        self.step_idx += 1

                elif current_step_name == "Features":
                    if k in ('UP', 'k'):
                        self.feature_cursor = (self.feature_cursor - 1) % len(self.feature_items)
                    elif k in ('DOWN', 'j'):
                        self.feature_cursor = (self.feature_cursor + 1) % len(self.feature_items)
                    elif k == 'SPACE':
                        self.feature_items[self.feature_cursor]['enabled'] = not self.feature_items[self.feature_cursor]['enabled']
                    elif k == 'ENTER':
                        self.step_idx += 1

                elif current_step_name == "Confirm":
                    if k == 'ENTER':
                        self.run_animated_install()
                        break
                    elif k in ('q', 'ESC'):
                        self.running = False
                        break

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, self.old_term)
            # Exit alternate screen buffer & restore cursor
            sys.stdout.write("\033[?1049l\033[?25h\033[0m")
            sys.stdout.flush()

# --- Fallback Line-by-Line Mode ---

def run_line_by_line_install(cli_args: Dict[str, Any]):
    env = get_system_environment()
    print(f"\n{C_BOLD}{C_CYAN}=== Terminal Welcome & SSH Tools Setup ==={C_RESET}")
    print(f"System: {env['distro']} | Python: {env['py_ver']} | User: {env['user_name']}\n")

    install_welcome = True
    install_sshm = True
    if not cli_args.get('all', False):
        if cli_args.get('welcome'):
            install_sshm = False
        elif cli_args.get('sshm'):
            install_welcome = False
        else:
            print("Choose components to install:")
            print(f"  1) All (Welcome Dashboard + Interactive SSH Manager sshm) {C_EMERALD}[Default]{C_RESET}")
            print("  2) Welcome Dashboard only (welcome)")
            print("  3) Interactive SSH Manager only (sshm)")
            try:
                ch = input("\nSelect option [1-3, default 1]: ").strip()
                if ch == '2':
                    install_sshm = False
                elif ch == '3':
                    install_welcome = False
            except (KeyboardInterrupt, EOFError):
                print(f"\n{C_ROSE}Installation cancelled.{C_RESET}")
                return

    user_name = cli_args.get('name')
    if install_welcome and not user_name:
        if cli_args.get('non_interactive') or cli_args.get('all') or not sys.stdin.isatty():
            user_name = env['user_name']
        else:
            try:
                inp = input(f"Preferred greeting display name [Default: {env['user_name']}]: ").strip()
                user_name = inp if inp else env['user_name']
            except (KeyboardInterrupt, EOFError):
                user_name = env['user_name']

    theme = cli_args.get('theme', 'tokyo-night')

    os.makedirs(TARGET_DIR, exist_ok=True)
    if install_welcome:
        welcome_src = os.path.join(BIN_DIR, 'welcome')
        os.chmod(welcome_src, 0o755)
        for s in ['welcome', 'motd', 'sysinfo', 'welcome-screen']:
            dest = os.path.join(TARGET_DIR, s)
            if os.path.islink(dest) or os.path.exists(dest):
                os.remove(dest)
            os.symlink(welcome_src, dest)
            print(f"  {C_EMERALD}✓{C_RESET} Linked {TARGET_DIR}/{s}")

        os.makedirs(USER_CONFIG_DIR, exist_ok=True)
        cfg = {
            'user_name': user_name or env['user_name'],
            'theme': theme,
            'show_temperature': True,
            'show_hosts': True,
            'show_ssh': True,
            'show_git': True,
            'show_notes': True,
            'show_services_alert': True,
            'max_hosts_preview': 4,
            'max_notes_preview': 3
        }
        with open(USER_CONFIG_FILE, 'w') as f:
            json.dump(cfg, f, indent=2)
        print(f"  {C_EMERALD}✓{C_RESET} Created configuration at {USER_CONFIG_FILE}")

        if not cli_args.get('no_hook'):
            hook_code = 'if [[ $- == *i* ]] && [ -x "$HOME/.local/bin/welcome" ]; then "$HOME/.local/bin/welcome"; fi'
            for rc in [os.path.expanduser('~/.bashrc'), os.path.expanduser('~/.zshrc')]:
                if os.path.exists(rc):
                    try:
                        with open(rc, 'r') as f:
                            c = f.read()
                        if "welcome" not in c:
                            with open(rc, 'a') as f:
                                f.write(f"\n# Terminal Welcome Dashboard\n{hook_code}\n")
                            print(f"  {C_EMERALD}✓{C_RESET} Added startup hook to {os.path.basename(rc)}")
                    except Exception:
                        pass

    if install_sshm:
        sshm_src = os.path.join(BIN_DIR, 'sshm')
        os.chmod(sshm_src, 0o755)
        for s in ['sshm', 'sshc', 'ssh-menu']:
            dest = os.path.join(TARGET_DIR, s)
            if os.path.islink(dest) or os.path.exists(dest):
                os.remove(dest)
            os.symlink(sshm_src, dest)
            print(f"  {C_EMERALD}✓{C_RESET} Linked {TARGET_DIR}/{s}")

    path_env = os.getenv('PATH', '')
    if TARGET_DIR not in path_env.split(':'):
        print(f"\n{C_AMBER}Note: {TARGET_DIR} is not currently in your PATH.{C_RESET}")
        print(f"Add this to your ~/.bashrc or ~/.zshrc:")
        print(f"  export PATH=\"$HOME/.local/bin:$PATH\"")

    print(f"\n{C_EMERALD}{C_BOLD}✓ Installation complete!{C_RESET}\n")

# --- Command Line Argument Parser ---

def parse_arguments() -> Dict[str, Any]:
    args = {
        'all': False,
        'welcome': False,
        'sshm': False,
        'name': '',
        'theme': 'tokyo-night',
        'non_interactive': False,
        'interactive': False,
        'no_hook': False,
        'help': False,
        'explicit_flag': False
    }

    it = iter(sys.argv[1:])
    for arg in it:
        if arg == '--all':
            args['all'] = True
            args['explicit_flag'] = True
        elif arg == '--welcome':
            args['welcome'] = True
            args['explicit_flag'] = True
        elif arg == '--sshm':
            args['sshm'] = True
            args['explicit_flag'] = True
        elif arg in ('--name', '-n'):
            try:
                args['name'] = next(it)
                args['explicit_flag'] = True
            except StopIteration:
                print(f"{C_ROSE}Error: --name requires a value.{C_RESET}")
                sys.exit(1)
        elif arg in ('--theme', '-t'):
            try:
                args['theme'] = next(it).lower()
                args['explicit_flag'] = True
            except StopIteration:
                print(f"{C_ROSE}Error: --theme requires a value.{C_RESET}")
                sys.exit(1)
        elif arg in ('--non-interactive', '-y', '--yes'):
            args['non_interactive'] = True
            args['explicit_flag'] = True
        elif arg in ('--interactive', '-i'):
            args['interactive'] = True
        elif arg == '--no-hook':
            args['no_hook'] = True
            args['explicit_flag'] = True
        elif arg in ('--help', '-h'):
            args['help'] = True
        else:
            print(f"{C_AMBER}Unknown option: {arg}{C_RESET}")
            args['help'] = True
            break

    return args

def print_help():
    print(f"""{C_BOLD}{C_CYAN}Terminal Suite Installer{C_RESET}
Usage: ./install.sh [OPTIONS]

{C_BOLD}Interactive Mode:{C_RESET}
  ./install.sh                Launch interactive setup wizard (default in terminal)
  ./install.sh -i             Force interactive wizard

{C_BOLD}CLI & Automated Options:{C_RESET}
  --all                       Install both Welcome Dashboard and SSH Manager
  --welcome                   Install only the Welcome Dashboard
  --sshm                      Install only the SSH Manager
  --name <name>               Set custom greeting display name
  --theme <theme>             Set color theme ({', '.join(THEMES.keys())})
  --non-interactive, -y       Run installation non-interactively with defaults
  --no-hook                   Skip adding automatic shell startup hooks
  --help, -h                  Show this help message
""")

def main():
    args = parse_arguments()

    if args['help']:
        print_help()
        sys.exit(0)

    is_tty = sys.stdin.isatty() and sys.stdout.isatty()
    should_interactive = False

    if args['interactive']:
        should_interactive = True
    elif is_tty and not args['non_interactive'] and not (args['all'] or args['welcome'] or args['sshm']):
        should_interactive = True

    if should_interactive and is_tty:
        try:
            wizard = InstallerWizard(args)
            wizard.run()
        except (KeyboardInterrupt, SystemExit):
            sys.stdout.write(f"\n{C_ROSE}Installation cancelled.{C_RESET}\n")
            sys.exit(0)
        except Exception as e:
            run_line_by_line_install(args)
    else:
        run_line_by_line_install(args)

if __name__ == '__main__':
    main()
