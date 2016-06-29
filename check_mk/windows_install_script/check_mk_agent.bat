@echo off

rem @author Alexander Zell <alexander.zell@hamcos.de>
rem @maintainer Robin Schneider <robin.schneider@hamcos.de>
rem @company hamcos IT Service GmbH http://www.hamcos.de
rem To download the setup file, run https://github.com/hamcos/monitoring-scripts/blob/master/check_mk/Makefile
rem This script is only needed if you do not use more appropriate means of configuration management.
rem
rem @license GPL-3.0 <https://www.gnu.org/licenses/gpl-3.0.html>
rem
rem This program is free software: you can redistribute it and/or modify
rem it under the terms of the GNU General Public License as published by
rem the Free Software Foundation, version 3 of the License.
rem
rem This program is distributed in the hope that it will be useful,
rem but WITHOUT ANY WARRANTY; without even the implied warranty of
rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
rem GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License
rem along with this program.  If not, see <https://www.gnu.org/licenses/>.

if exist "%programfiles%\check_mk\check_mk_agent.exe" goto installed
if exist "%programfiles(x86)%\check_mk\check_mk_agent.exe" goto installed

rem Check for root permissions {{{
rem http://stackoverflow.com/a/11995662
echo Administrative permissions required. Detecting permissions ...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Success: Administrative permissions confirmed.
) else (
    echo Failure: Current permissions inadequate.
    echo Please execute with administrative permissions.
    pause
    exit
)
rem }}}

rem Switch to `dirname $0` {{{
rem Windows hack to execute all following instruction in context of the directory form where the script is located.
rem https://social.technet.microsoft.com/Forums/scriptcenter/en-US/360ff40b-6a2b-4651-9a3e-360e803d8ffb/executing-batch-file-as-administrator-changes-working-directory?forum=ITCG
@setlocal enableextensions
@cd /d "%~dp0"
echo Executing script in context of %cd%
rem }}}

echo Install agent without user interaction.
.\check_mk_agent.msi /passive

echo Ensure that the agent is stopped.
net stop Check_MK_Agent

rem Configure firewall {{{
echo Add firewall rule to allow external access to the agent. Note that this will add a new rule each time it is executed (not idempotent).
netsh advfirewall firewall add rule name="Check_MK_Agent" dir=in action=allow protocol=TCP localport=6556 enable=yes

echo Add firewall rule to allow ICMP echo request to the host.

netsh advfirewall firewall set rule name="File and Printer Sharing (Echo Request - ICMPv4-In)" new enable=yes

rem https://superuser.com/questions/342822/enable-ping-in-windows-7-firewall/343111#343111
rem Do not use this explicit rule because the IPv6 equivalent seems not to work.
rem netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol=icmpv4:8,any dir=in action=allow
echo Ensure deprecated firewall rules are absent
netsh advfirewall firewall delete rule name="ICMP Allow incoming V4 echo request"


netsh advfirewall firewall set rule name="File and Printer Sharing (Echo Request - ICMPv6-In)" new enable=yes

rem Although it is documented by https://technet.microsoft.com/de-de/library/ee382272%28v=ws.10%29.aspx it throws: "A specified protocol value is not valid."
rem Well done MS …
rem And yes, ICMPv6 echo request was filtered by the firewall by default …
rem netsh advfirewall firewall add rule name="ICMP Allow incoming V6 echo request" protocol=icmpv6:128,0 dir=in action=allow

rem }}}

rem Configure on x86-32 systems {{{
if exist "%programfiles(x86)%" goto x64
echo Configure agent on a x86-32 system.
mkdir "%programfiles%\check_mk"
copy .\check_mk.ini "%programfiles%\check_mk\check_mk.ini" /y
net start Check_MK_Agent
goto ende
rem }}}

rem Configure on x86-64 systems {{{
:x64
echo Configure agent on a x86-64 system.
mkdir "%programfiles(x86)%\check_mk"
copy .\check_mk.ini "%programfiles(x86)%\check_mk\check_mk.ini" /y
net start Check_MK_Agent
goto ende
rem }}}

:installed
echo Agent was already installed.

:ende
pause
