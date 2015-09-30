# https://mathias-kettner.de/check_mk_download_source.html
#
VERSION ?= 1.2.6p12

.PHONY: default clean
default: windows_install_script/install_agent-64.exe

clean:
	rm -rf check_mk-*

check_mk-$(VERSION).tar.gz:

check_mk-%.tar.gz:
	wget "https://mathias-kettner.de/download/$@"

check_mk-$(VERSION):

check_mk-%: check_mk-%.tar.gz
	tar xzf "$@.tar.gz"

check_mk-$(VERSION)/windows:

check_mk-%/windows: check_mk-%
	cd "$(shell dirname $@)" && tar xzf agents.tar.gz

windows_install_script/install_agent-64.exe: check_mk-$(VERSION)/windows/check_mk_agent-64.exe
	cp "$<" "$@"
