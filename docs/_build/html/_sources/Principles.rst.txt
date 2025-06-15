Basic principles
================

The project is based on few principles:

* An observation is a consistent set of images and data, collected in an Observation File (yaml format)... or json? YAML pour les commentaires ?
* All files of one observing night are saved in a single folder
* All images and spectra are in FTIS format (which is THE format for astronomy files).
* We use only Open Source tools:

  * Linux.
  * Python (3.10 or above) as much as possible.
  * Git for revision control and sharing the code.
  * Rest API interfaces (to split front-end and back-end).
  * User interfaces in (JavaScript / TypeScript).
  * INDI server and devices (INDI is for Linux what ASCOM is for Windows).
  * Sphinx for the documentation.
  * Few standard Python libraries :

    * Astropy, for all Astronomy related stuff.
    * FastAPI for the Rest API interfaces.
    * MQTT and TIG (Telegraf / InfluxDB / Grafana) to reacord real time data.
    * Logging for the loggers (all actions are recorded).
    * PyTransitions (for Finite States Machine).
    * Cmd.cmd (for getting a command line interface (CLI), useful for debugging).

* The dome or shelter can open and close whatever is the telescope position.
* Each module can be installed locally or remotely (client-server architecture).
* We can use Kstars for monitoring the actions (very useful for debugging).
* We love the concept of continuous improvement ; a small step every day.

* There is a single configuration file (in yaml format) for each module.
