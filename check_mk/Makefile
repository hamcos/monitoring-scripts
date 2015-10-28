# https://mathias-kettner.de/check_mk_download_source.html
#
VERSION ?= 1.2.6p12

.PHONY: default clean
default: copy-agent

copy-agent: windows_install_script/check_mk_agent.exe \
	windows_install_script/check_mk_agent-64.exe \
	windows_install_script/check_mk_agent.msi \
	windows_install_script/install_agent.exe \
	windows_install_script/install_agent-64.exe \
	windows_install_script/mrpe/ \
	windows_install_script/plugins/

clean:
	rm -rf check_mk-*

check_mk-$(VERSION).tar.gz:

check_mk-%.tar.gz:
	wget "https://mathias-kettner.de/download/$@"

check_mk-$(VERSION):

check_mk-%: check_mk-%.tar.gz
	tar xzf "$@.tar.gz"

check_mk-$(VERSION)/windows:

check_mk-%/windows/check_mk_agent-64.exe: check_mk-%/agents.tar.gz
	cd "$(@:%/windows/check_mk_agent-64.exe=%)" && tar xzf agents.tar.gz

windows_install_script/%: check_mk-$(VERSION)/windows/%
	cp -r "$<" "$@"
