# Control PC Using Gmail
Remote control personal computer using Gmail API
## REQUEST format: Subject - Context
* Shutdown: SHUTDOWN - [time format hh:mm:ss]
* Restart: RESTART - [time format hh:mm:ss]
* Copy file: COPY FILE - [file path] \n [destination path]
* Capture screen: SCREEN CAPTURE - [anything or blank]
* Capture webcam: WEBCAM CAPTURE - [anything or blank]
* List running processes: LIST PROCESSES - [anything or blank]
* Kill a process: KILL PROCESS - [process name format: process_name.exe]
* Detect keypress from user: KEYPRESS - [number of seconds]
* Edit value of a registry key: REGISTRY KEY - [delete | set] \n [registry key's path] \n [the value] \n [value type]

**MUST INCLUDE SECRET KEY IN CONTEXT (in the first line of email context)**: *019250304*
## RESPONSE format: Subject - Context
* Shutdown: SHUTDOWN - "The computer is scheduled to shutdown at @time."
* Restart: RESTART - "The computer is scheduled to restart at @time."
* Copy file: COPY FILE - [new file path]
* Capture screen: SCREEN CAPTURE - [embed screen image]
* Capture webcam: WEBCAM CAPTURE - [embed webcam image]
* List running processes: LIST PROCESSES - [a list of running processes]
* Kill a process: KILL PROCESS - [command prompt result]
* Detect keypress from user: KEYPRESS - [keypress list]
* Edit value of a registry key: REGISTRY KEY - [system result]