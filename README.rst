state\_machine
==============

state machine for humans

|Build Status|

There are two types of developers in this world: those who love state
machines and those who *will* eventually.

I fall in the first camp. I think it is really important to have a
declarative way to define the states of an object. That’s why I
developed ``state_machine``.

Install
-------

.. code:: bash

    pip install state_machine

.. |Build Status| image:: https://travis-ci.org/jtushman/state_machine.svg?branch=master
   :target: https://travis-ci.org/jtushman/state_machine

Basic Usage
-----------

.. code:: python


    @acts_as_state_machine()
    class Person():
        name = 'Billy'

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('sleep')
        def do_one_thing(self):
            print "{} is sleepy".format(self.name)

        @before('sleep')
        def do_another_thing(self):
            print "{} is REALLY sleepy".format(self.name)

        @after('sleep')
        def snore(self):
            print "Zzzzzzzzzzzz"

        @after('sleep')
        def big_snore(self):
            print "Zzzzzzzzzzzzzzzzzzzzzz"

    person = Person()
    print person.current_state == Person.sleeping       # True
    print person.is_sleeping                            # True
    print person.is_running                             # False
    person.run()
    print person.is_running                             # True
    person.sleep()

    # Billy is sleepy
    # Billy is REALLY sleepy
    # Zzzzzzzzzzzz
    # Zzzzzzzzzzzzzzzzzzzzzz

    print person.is_sleeping                            # True

Features
--------

Before / After Callback Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add callback hooks that get executed before or after an event
(see example above).

*Important:* if the *before* event causes an exception or returns
``False``, the state will not change (transition is blocked) and the
*after* event will not be executed.

Blocks invalid state transitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An *InvalidStateTransition Exception* will be thrown if you try to move
into an invalid state.

Name of the state field
~~~~~~~~~~~~~~~~~~~~~~~

The default name of the state field is "aasm_state". 
If the field already exist in the object il will be used as so (beware to initialize it with the default state value yourself in the init function)
If you want to change it, you just have to give it as  an argument to the acts_as_state_machine decorator:
    @acts_as_state_machine('my_field_name')
    class Person():
		...

ORM support
-----------

It should be done independently


Issues / Roadmap:
-----------------

-  Allow multiple state\_machines per object

Questions / Issues
------------------

Feel free to ping me on twitter: `@tushman`_
or add issues or PRs at https://github.com/jtushman/state_machine

.. _@tushman: http://twitter.com/tushman

Thank you
---------

to `aasm`_ and ruby’s `state\_machine`_ and all other state machines
that I loved before

.. _aasm: https://github.com/aasm/aasm
.. _state\_machine: https://github.com/pluginaweek/state_machine

