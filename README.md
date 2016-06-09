# ansible-vnx
Ansible-module of VNX

### Directory Structure
```
|--README.md
|--host_vars
|  |--admin.nsdom.local		Configuration Parameters
|--hosts			Management Server IPs
|--library
|  |--cachechk.py		Check Cache Status
|  |--diskchk.py		Check Disk Status
|  |--faultschk.py		Check Fault Status
|  |--hwchk.py			Check Hardware Status
|  |--sg.py			Create Storagegroup
|  |--sghost.py			Setting of Storagegroup Hosts
|  |--sglun.py                  Setting of Storagegroup LUNs
|--roles
|  |--health_check
|  |  |--tasks
|  |  |  |--main.yml		Task List of Health Check
|  |  |--vars
|  |  |  |--main.yml		Parameters of Health Check
|  |--masking
|  |  |--tasks
|  |  |  |--main.yml		Task List of Masking
|  |  |--vars
|  |  |  |--main.yml		Parameters of Masking
|--site.yml
```
