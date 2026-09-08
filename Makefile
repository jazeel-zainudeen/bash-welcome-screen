.PHONY: help install install-welcome install-sshm uninstall test check

help:
	@echo "Terminal Suite - Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make install          Install all components (welcome + sshm)"
	@echo "  make install-welcome  Install only the welcome dashboard"
	@echo "  make install-sshm     Install only the sshm connection manager"
	@echo "  make uninstall        Uninstall all components"
	@echo "  make test             Validate Python syntax of all executables"
	@echo ""

install:
	@./install.sh --all

install-welcome:
	@./install.sh --welcome

install-sshm:
	@./install.sh --sshm

uninstall:
	@./uninstall.sh --all

test: check

check:
	@python3 -m py_compile bin/welcome bin/sshm
	@echo "✓ All scripts passed Python syntax check."
