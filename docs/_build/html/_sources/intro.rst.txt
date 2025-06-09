Introduction
============

This project proposes to setup your own robotic observatory for Astronomical Spectro observations.

A proposal : the name of the project is ROSACE, for **Robotic Observations and Spectrocopic Astronomy, a Collaborative Experience**

Our intention is that many observers, with different instruments and for various scientific programs can use this system. The final goal is that we can produce
all together valuable data for the science, and at the end for better understand the Universe we're living in.

We do think that Spectroscopic observations **cannot be fully standard**. The observation sequence will depend on your own setup, and the data reduction will
vary from one scientific goal to the other. You will probably have to 'put your hands on', and write some code to adapt the system to your own need. We want
to make these adaptations as simple as possible.

To make this system accessible for everyone, we've organized with independant modules, with few general rules, and the code is intended to be easy
to read and to maintain. Managing several small problems is better than a big one. 

We work over the long term. People will change, instruments will change, new science opportunities will arise. The platform must be able to adapt
to all these changes. To make this, we do our best to be clear on what is stable over the time (for instance the Observing File format), and what can 
evolve (the instruments, the observing sequences, and so on).

We think that continous improvement is the best way to move forward - one small step everyday. 

The system is made of 5 independant modules:

* Module 1: The dome/shelter control
* Module 2: Shelduler (what is the next target to observe)
* Module 3: Sequencer (run the actual observation)
* Module 4: Data reduction (to get a scientific result)
* Module 5: Display and share the results

