# Control PC Using Gmail
Remote control personal computer using Gmail API
## REQUEST format: Subject - Context
* Shutdown: SHUTDOWN - [time format hh:mm:ss]
* Restart: RESTART - [time format hh:mm:ss]
* Copy file: COPY FILE - [file path] \n [destination path]
* Capture screen: CAPTURE - [anything or blank]
* List running processes: RUNNING PROCESSES - [anything or blank]
* Kill a process: KILL PROCESS - [process name]
* Getting input keyboard: CATCH KEYS - [number of seconds]
* Registry entry:

**MUST INCLUDE SECRET KEY IN CONTEXT**: *019250304*
## RESPONSE format: Subject - Context
* Shutdown: SHUTDOWN - "The computer is shut down."
* Restart: RESTART - "The computer is restarted."
* Copy file: COPY FILE - [new file path]
* Capture screen: CAPTURE - [embed screen image]
* List running processes: RUNNING PROCESSES - [a list of processes' name]
* Kill a process: KILL PROCESS - [successful / failed (included failed message if possible)]
* Getting input keyboard: CATCH KEYS - [keys input]
* Registry entry: