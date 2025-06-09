Basic principles
================

The project is based on few principles:

* We use only Open Source tools:

  * Linux
  * Python (3.10 or above) as much as possible
  * Rest API interfaces (to split front-end and back-end)
  * User interfaces in (JavaScript / TypeScript)
  * INDI server and devices (INDI is for Linux what ASCOM is for Windows)
  * Sphinx for the documentation
  * Few standard Python libraries :

    * Astropy, for all Astronomy related stuff
    * FastAPI for the Rest API interfaces
    * MQTT and TIG (Telegraf / InfluxDB / Grafana) to reacord real time data
    * Logging for the loggers (all actions are recorded)
    * PyTransitions (for Finite States Machine)

* The dome or shelter can open and close whatever is the telescope position.
* Each module can be installed locally or remotely (client-server architecture)
* We use Kstars for monitoring the actions (very useful for debugging)
