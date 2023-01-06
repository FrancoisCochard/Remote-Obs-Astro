# RemoteObservatory
[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

TODO TN: Currently in ugly debug mode to check for calibration behaviour: #TODO TN DEBUG

Another astronomical observatory manager.
This project either uses, or is directly inspired by:

* KStars: https://github.com/KDE/kstars
* Indi: https://github.com/indilib/indi (Jasem Mutlaq + contributors)
* Starquew: https://github.com/GuLinux/StarQuew/tree/master/backend/indi (Marco Gulino)
* npindi: https://github.com/geehalel/npindi (Geehalel)
* Panoptes: https://github.com/panoptes/POCS
* Astropy: https://github.com/astropy/astropy
* Astroplan: https://github.com/astropy/astroplan (Brett Morris + contributors)
* Astrometry.net: https://github.com/dstndstn/astrometry.net (Dustin Lang + contributors)
* PHD2: https://github.com/OpenPHDGuiding/phd2/wiki/EventMonitoring
* notebooks from ivandga for amateur spectroscopy: https://github.com/ivandga/ArasSpectraNotebooks
* SpectroStars from Serge Golovanow: https://github.com/serge-golovanow/SpectroStars
* Astroalign: https://github.com/toros-astro/astroalign
* Aladin-lite (mostly for PAWS actually): https://github.com/cds-astro/aladin-lite
* MMTO Observatory indi client: https://github.com/MMTObservatory/indiclient
* Meshcat: https://github.com/rdeits/meshcat-python but we might want to replace meshcat with scenepic in the future: https://microsoft.github.io/scenepic/python/

# Install

## System requirements when using ubuntu
```bash
sudo apt-add-repository ppa:mutlaqja/ppa
sudo add-apt-repository ppa:pch/phd2
sudo apt-get update
sudo apt-get install \
    astrometry-data-4208-4219\
    extra-cmake-modules\
    gpsd\
    indi-full\
    kdelibs5-dev\
    kdoctools-dev\
    kstars-bleeding\
    libastrometry*\
    libboost-dev\
    libboost-regex-dev\
    libcfitsio-dev\
    libcurl4-openssl-dev\
    libfftw3-dev\
    libftdi-dev\
    libftdi1-dev\
    libgphoto2-dev\
    libgps-dev\
    libgraphviz-dev \
    libgsl-dev\
    libindi-dev\
    libindi1\
    libjpeg-dev\
    libkf5configwidgets-dev\
    libkf5crash-dev\
    libkf5declarative-dev\
    libkf5globalaccel-dev\
    libkf5kdelibs4support5-bin\
    libkf5newstuff-dev\
    libkf5notifications-dev\
    libkf5notifyconfig-dev\
    libkf5plotting-dev\
    libkf5windowsystem-dev\
    libkf5xmlgui-dev\
    libnova*\
    libogg-dev\
    libpython3-dev\
    libqt5svg5-dev\
    libqt5websockets5-dev\
    libraw-dev\
    librtlsdr-dev\
    libtheora-dev\
    libtiff-dev\
    libusb-1.0-0-dev\
    libwxgtk3.0-dev\
    phd2\
    qttools5-dev-tools\
    swig3.0\
    wcslib-dev\
    xplanet\
    zlib1g-dev\
    -y
```

## Setup virtual environment

```console
    pip install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

## Building the nice reporting / latex reports
```bash
  sudo apt-get update
  sudo apt-get install -y texlive-latex-recommended texlive-publishers texlive-bibtex-extra texlive-science
```
Then build with
```console
  python setup.py gen_report
```

## Python requirements
pip install Cython setuptools wheel requests pyindi-client requests-cache watchdog astropy ntplib astroplan matplotlib tzwhere astroquery pymongo rawpy serial pyserial socket astroalign
If you want to run the astrometry server locally, use:
pip install django Pillow

## Kafka GCN stuff
```console
  sudo apt-get install libzstd-dev
  sudo apt-get install libz-dev
  sudo apt-get install rapidjson-dev
  sudo apt-get -y install libsasl2-dev
  sudo apt-get -y install libssl-dev
  git clone https://github.com/edenhill/librdkafka
  cd ./librdkafka
  git checkout v1.9.2-RC3
  ./configure && make -j8 && sudo make install && ldconfig
  pip install --no-binary :all: confluent-kafka
```

## Arduino stuff
If you are interested in compiling/using the arduino stuff here, please download the official Arduino IDE, and define the following environment variable: $ARDUINO_SDK_PATH

```console
  export ARDUINO_SDK_PATH="/opt/arduino-1.8.19/"
  cd Arduino
  mkdir build && cd build
  cmake ..
  make
  cd ..
  ./upload.sh
```


## Setup indiweb on the machine that will host drivers
check installation information on: https://github.com/knro/indiwebmanager
pip install indiweb
sudo cp indiwebmanager.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/indiwebmanager.service
sudo systemctl daemon-reload
sudo systemctl enable indiwebmanager.service

content of indiwebmanager.service
```bash
# From https://github.com/knro/indiwebmanager
# sudo pip install indiweb
# sudo cp indiwebmanager.service /etc/systemd/system/
# sudo chmod 644 /etc/systemd/system/indiwebmanager.service
# sudo systemctl daemon-reload
# sudo systemctl enable indiwebmanager.service
# sudo reboot
# sudo systemctl status indiwebmanager.service

[Unit]
Description=INDI Web Manager
After=multi-user.target

[Service]
Type=idle
# MUST SET YOUR USERNAME HERE.

User=rock
ExecStart=/usr/local/bin/indi-web -v --xmldir /home/user/projects/RemoteObservatory/conf_files/indi_driver_conf
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

# Specific case of aarch64 kernel and armv8 userland
go to your set of build directories:
* indi-altair
* indi-duino
* indi-libaltaircam
* indi-toupbase
* libmallincam
* libstarshootg
* indi
* indi-asi
* indi-gphoto
* indi-shelyak
* libASICamera2
* libnncam
* libtoupcam
Then edit CMakeFiles/3.7.2/CMakeSystem.cmake
replace aarch64 by armv8

# How to launch the full stuff

## If you want to try the software with simulators:
./apps/launch_indi_simu.sh
PYTHONPATH=. python ./apps/launch_remote_observatory.py

## If, in addition you want the nice dashboard (might require additional dependencies, scripts are untested)
./apps/launch_PAWS.sh
PYTHONPATH=. python ./apps/launch_qt_dashboard.py
PYTHONPATH=. python3 ./apps/launch_weather_capture.py (only a stub for now)


## Legacy or optional features
### Support for DBus scripting ()
sudo apt-get install libgirepository1.0-dev gobject-introspection
pip install PyGObject
or
conda install -c conda-forge pygobject
### Support for the Dash dashboard (legacy, not used anymore):
pip install dash dash-core-components dash-html-components dash-renderer plotly
### Web service (legacy, not used anymore)
For now, RemoteObservatory uses some web service to acquire data, so ensure that you have a json file containing the key for each API in your home directory:
  * For WUG, get your key [here](https://www.wunderground.com/weather/api/) and store it in your home directory inside a .wug.json file
  * For nova (astrometry.net), get your key at [here](http://nova.astrometry.net/api_help) and store it in your home directory inside a .nova.json file
### Arduino capture
PYTHONPATH=. python3 ./apps/launch_arduino_capture.py


## TODO: WORK IN PROGRESS: Check before calling this a production software
* make sure we are correctly scoring all constraints (not only binary values) in ObservationPlanner/Scheduler
* Correct the stub inside of launch_remote_observatory that returns safe even if not safe
* re-integrate the simulator mode that returns fine, even if not fine
* Make a proper integration between our IndiMount and abstractMount inside of IndiAbstractMount, because right now it is a mess
* Setup a calibrating_flat and calibrating_dark states
* fill-in the class Calibration that mirrors the observation class and make sure  that a new calibration is issued whenever an observation has completed (This should arise in Manager ?)
* Check why the SITELONG entry in outputed file is wrong
* ObservationPlanner/Scheduler l232 you NEED to setup proper FixedTarget.from_name
* ShedObservatory l76: uncomment the raise ScopeControllerError(msg)
* Gast is important: Service/NTPTimeService.py l 137
* Urgent: fix the hardcoded values in solve-field scripting
* Urgent fix the max_pointing_error in pointing. Current one might be too low
* L292 in StateMachine, find a better way to signal the issue when transitionning
* Remove temporary fix in Scheduler:             target = FixedTarget(SkyCoord(ra=1*u.deg, dec=89*u.deg)
* Need to try to kill PHD2 while guiding and check that we return to parking state
* Need to simulate a PHD2 star lost and check that we return to parking state
* The loop_mode in GuiderPHD2 is ambiguous (let it like this for now)
* Check all states from the state machine, and make sure they often call model.check_messages()
* If an observation is split into multiple observing block, shouldn't they have the same id ? that would allow to skip pointing when going from one block to another
* check if we actually refocus in case the observation id is the same
* the publisher_port parameter in weather config should be refactored with messaging parameter
* PHD2 is not closed properly / two instance might be launched which cause error
* Transform the Manager.acquire_calibration into a generator, so that every acquisition is yielded toward the State, and it may issue messages in the meantime
* AbstractCamera (and potentially other classes based on BASE) have its self.config attribute overwritten somewhere ? it evaluates to None at some point, so it needs investigation
* indiclient parser and PHD2 client parser are almost the same... You need to abstract away the XML client part and make a single class for this



# Helper
* use find . -path ./venv -prune -o -name '*.py' to search stuf not in venv
* use find . -path ./venv -prune -o -name '*.py' -exec grep -H string_to_find {} \;
* use find . -path ./venv -prune -o -name '*.py' -exec sed -i -e 's/get_local_time_from_ntp/get_local_time/g' {} \; to replace stuff
