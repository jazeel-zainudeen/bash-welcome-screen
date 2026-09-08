.PHONY: help install install-interactive install-welcome install-sshm uninstall test check

help:
	@echo "Terminal Suite - Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make install              Install all components (welcome + sshm)"
	@echo "  make install-interactive  Launch interactive setup wizard"
	@echo "  make install-welcome      Install only the welcome dashboard"
	@echo "  make install-sshm         Install only the sshm connection manager"
	@echo "  make uninstall            Uninstall all components"
	@echo "  make test                 Validate Python syntax of all executables"
	@echo ""

install:
	@./install.sh --all --non-interactive

install-interactive:
	@./install.sh -i

install-welcome:
	@./install.sh --welcome --non-interactive

install-sshm:
	@./install.sh --sshm --non-interactive

uninstall:
	@./uninstall.sh --all

test: check

check:
	@python3 -m py_compile bin/welcome bin/sshm scripts/installer.py
	@echo "✓ All scripts passed Python syntax check."

