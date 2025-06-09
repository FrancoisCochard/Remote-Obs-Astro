Module 3: Sequencer
===================

The module is part of the :ref:`Obervatory <MainPage>`

This module is the core of the Robotic observation. It runs all the steps of an observation sequence.

Each observation runs a given observing sequence. You can write your own sequence, to match your scientific need. The sequence is made of "bricks" ; 
you can use existing bricks or write your owns.

Here are the main (and required) principles for this module:

#. Each observation uses a specific sequence (mainly linked to the scientific goal of the observation).
#. A sequence is a single list of basic steps. No loops, no conditions, the system is very rustic.
#. A single structure is used to give each step all the data it needs (target star, exposure duration, and so on).
#. This structure can be append by each step.
#. This structure is also used at the end of the process to write the "Observing file", needed for the data reduction.
#. We use a common logger system ; each step can log any data it wants.
#. Each step ends by a standard 'return', that allow the sequence to continue, or to stop if a problem occured.