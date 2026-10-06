PREFIX ?= /usr/local
ZSH_COMPLETION_DIR ?= $(PREFIX)/share/zsh/site-functions

.PHONY: test lint install uninstall deb

test:
	python3 tests/test_cpath.py

lint:
	shellcheck bin/cpath scripts/*.sh

install:
	install -d "$(DESTDIR)$(PREFIX)/bin" "$(DESTDIR)$(ZSH_COMPLETION_DIR)"
	install -m 755 bin/cpath "$(DESTDIR)$(PREFIX)/bin/cpath"
	install -m 644 completions/_cpath "$(DESTDIR)$(ZSH_COMPLETION_DIR)/_cpath"

uninstall:
	rm -f "$(DESTDIR)$(PREFIX)/bin/cpath" "$(DESTDIR)$(ZSH_COMPLETION_DIR)/_cpath"

deb:
	./scripts/build-deb.sh
