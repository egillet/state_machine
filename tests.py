import functools
import os
import nose
from nose.plugins.skip import SkipTest
from nose.tools import *
from nose.tools import assert_raises


from state_machine import acts_as_state_machine, before, State, Event, after, InvalidStateTransition

###################################################################################
## Plain Old In Memory Tests
###################################################################################

def test_state_machine():
    @acts_as_state_machine()
    class Robot():
        name = 'R2-D2'

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('sleep')
        def do_one_thing(self):
            print("{} is sleepy".format(self.name))

        @before('sleep')
        def do_another_thing(self):
            print("{} is REALLY sleepy".format(self.name))

        @after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzz")

        @after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzzzzzzzzzzzz")


    robot = Robot()
    eq_(robot.current_state, 'sleeping')
    assert robot.is_sleeping
    assert not robot.is_running
    robot.run()
    assert robot.is_running
    robot.sleep()
    assert robot.is_sleeping



def test_named_state_machine():
    @acts_as_state_machine('state')
    class Robot():
        name = 'R2-D2'

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('sleep')
        def do_one_thing(self):
            print("{} is sleepy".format(self.name))

        @before('sleep')
        def do_another_thing(self):
            print("{} is REALLY sleepy".format(self.name))

        @after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzz")

        @after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzzzzzzzzzzzz")


    robot = Robot()
    eq_(robot.current_state, 'sleeping')
    assert robot.is_sleeping
    assert not robot.is_running
    robot.run()
    assert robot.is_running
    robot.sleep()
    assert robot.is_sleeping


def test_state_machine_no_callbacks():
    @acts_as_state_machine()
    class Robot():
        name = 'R2-D2'

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

    robot = Robot()
    eq_(robot.current_state, 'sleeping')
    assert robot.is_sleeping
    assert not robot.is_running
    robot.run()
    assert robot.is_running
    robot.sleep()
    assert robot.is_sleeping


def test_named_state_machine_no_callbacks():
    @acts_as_state_machine('state')
    class Robot():
        name = 'R2-D2'

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

    robot = Robot()
    eq_(robot.current_state, 'sleeping')
    assert robot.is_sleeping
    assert not robot.is_running
    robot.run()
    assert robot.is_running
    robot.sleep()
    assert robot.is_sleeping


def test_multiple_machines():
    @acts_as_state_machine()
    class Person(object):
        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('run')
        def on_run(self):
            things_done.append("Person.ran")

    @acts_as_state_machine()
    class Dog(object):
        sleeping = State(initial=True)
        running = State()

        run = Event(from_states=sleeping, to_state=running)
        sleep = Event(from_states=(running,), to_state=sleeping)

        @before('run')
        def on_run(self):
            things_done.append("Dog.ran")

    things_done = []
    person = Person()
    dog = Dog()
    eq_(person.current_state, 'sleeping')
    eq_(dog.current_state, 'sleeping')
    assert person.is_sleeping
    assert dog.is_sleeping
    person.run()
    eq_(things_done, ["Person.ran"])

def test_multiple_named_machines():
    @acts_as_state_machine('state0')
    class Person(object):
        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('run')
        def on_run(self):
            things_done.append("Person.ran")

    @acts_as_state_machine('state1')
    class Dog(object):
        sleeping = State(initial=True)
        running = State()

        run = Event(from_states=sleeping, to_state=running)
        sleep = Event(from_states=(running,), to_state=sleeping)

        @before('run')
        def on_run(self):
            things_done.append("Dog.ran")

    things_done = []
    person = Person()
    dog = Dog()
    eq_(person.current_state, 'sleeping')
    eq_(dog.current_state, 'sleeping')
    assert person.is_sleeping
    assert dog.is_sleeping
    person.run()
    eq_(things_done, ["Person.ran"])


if __name__ == "__main__":
    nose.run()
