@echo off
for /l %%i in (0,1,0) do start cmd /k "echo %%i&&python3 C:\smartDev\smart_dev.py -i 192.168.0.86 -t 95 -x %%i -c 100"
for /l %%i in (100,1,100) do start cmd /k "echo %%i&&python3 C:\smartDev\smart_dev.py -i 192.168.0.86 -t 95 -x %%i -c 100"
for /l %%i in (200,1,200) do start cmd /k "echo %%i&&python3 C:\smartDev\smart_dev.py -i 192.168.0.86 -t 95 -x %%i -c 100"
for /l %%i in (300,1,300) do start cmd /k "echo %%i&&python3 C:\smartDev\smart_dev.py -i 192.168.0.86 -t 95 -x %%i -c 100"

