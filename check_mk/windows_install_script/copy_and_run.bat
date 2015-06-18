@echo off
rem needed because cmd is incapable of executing the install script from an UNC path.

xcopy "\\WEDERTVSRV008\mon" C:\_service_it\mon /D /E /C /R /H /I /K /Y
cd C:\_service_it\mon
.\check_mk_agent.bat
