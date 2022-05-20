# Control PC Using Gmail
Remote control personal computer using Gmail API
## REQUEST format: Subject - Context
* Shutdown: SHUTDOWN - [time format hh:mm:ss]
* Restart: RESTART - [time format hh:mm:ss]
* Copy file: COPY FILE - [file path] \n [destination path]
* Capture screen: CAPTURE - [anything or blank]
* Capture webcam:
* List running processes: RUNNING PROCESSES - [anything or blank]
* Kill a process: KILL PROCESS - [process id]
* Getting input keyboard: CATCH KEYS - [number of seconds]
* Registry entry:

**MUST INCLUDE SECRET KEY IN CONTEXT (in the first line of email context)**: *019250304*
## RESPONSE format: Subject - Context
* Shutdown: SHUTDOWN - "The computer is scheduled to shutdown at @time."
* Restart: RESTART - "The computer is scheduled to restart at @time."
* Copy file: COPY FILE - [new file path]
* Capture screen: CAPTURE - [embed screen image]
* Capture webcam:
* List running processes: RUNNING PROCESSES - [a csv file contains info about running processes]
* Kill a process: KILL PROCESS - [successful + running processes after kill process / failed (included failed message if possible)]
* Getting input keyboard: CATCH KEYS - [keys input]
* Registry entry: