# Scimitar
## Ye Distributed Debugger

### GDB Integration
* The scripts are in the
  [tools](`https://github.com/STEllAR-GROUP/scimitar/tree/master/tools`) directory.
* To import the printers:
    * If your GDB is set up to perform auto loading simply copy `auto-load` and
      `python` directories to the appropriate locations.
    * If you're not using auto-load then ensure the path to auto-load and
      Python directories are in `sys.path`
        * One option to add them to GDB Python's sys.path is running `python
          sys.path.append(`'<PATH_TO_DIR>'`)` for both directories.
    * Run `python import scimitar_gdb` inside GDB
    * You can also put the commands inside your `.gdbrc`

```
python
sys.path.extend([
    '<path to scimitar-gdb directory>/auto-load',
    '<path to scimitar-gdb directory>/python',
])
import scimitar_gdb
end
```

### Prerequisites
* Software:
  * Python 2.7 (Previous versions not tested. Might work fine)
  * GDB 7.1 (Previous versions not tested. Might work fine)
* Python Modules
  * pexpect

### Configuration
In order to prevent having to enter the debugging environment configurations
every time it is launched and save time Scimitar uses the file
`config.py` to retrieve the configurations of a cluster. You may modify
and add to it to meet your needs.

### Running
* Make sure your application is running and mpirun has started.
* Run `scimitar.py` on your machine
* Start a session by `job <scheduler_job_id> <application_name>`
* Once you're connected you can switch between localities by using the command
  `switch <locality_id>`
* You can see the list of active localities with `ls` command.
