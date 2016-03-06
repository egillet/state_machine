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
        def do_one_thing(self, param):
            print "{} is sleepy".format(self.name)

        @before('sleep')
        def do_another_thing(self, param):
            print "{} is REALLY sleepy and will sleep {}".format(self.name, param)

        @after('sleep')
        def snore(self, param):
            print "Zzzzzzzzzzzz"

        @after('sleep')
        def big_snore(self, param):
            print "Zzzzzzzzzzzzzzzzzzzzzz (%r)"%param

    person = Person()
    print person.current_state == Person.sleeping       # True
    print person.is_sleeping                            # True
    print person.is_running                             # False
    person.run()
    print person.is_running                             # True
    person.sleep('a long time')

    # Billy is sleepy
    # Billy is REALLY sleepy and will sleep a long time
    # Zzzzzzzzzzzz
    # Zzzzzzzzzzzzzzzzzzzzzz (a long time)

    print person.is_sleeping                            # True

Features
--------

Before / After Callback Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add callback hooks that get executed before or after an event
(see example above).
If a event is called with parameters, all the before/after callback must be defined with a compatible signature

*Important:* if the *before* event causes an exception or returns
``False``, the state will not change (transition is blocked) and the
*after* event will not be executed.

Blocks invalid state transitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An *InvalidStateTransition Exception* will be thrown if you try to move
into an invalid state.

Name of the state field
~~~~~~~~~~~~~~~~~~~~~~~

The default name of the state field is "aasm_state". If you want to chane it, you just have to give it as  an argument to the acts_as_state_machine decorator:
    @acts_as_state_machine('my_field_name')
    class Person():
		...

ORM support
-----------

No more support for ORM, just plain old object. 
If the state field preexists, it's reused and you must give the default value at the initialization else it's created and initialized to the name of the default State.


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

Contents:

.. toctree::
   :maxdepth: 2

