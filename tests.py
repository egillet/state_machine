import functools
import os
import nose
from nose.plugins.skip import SkipTest
from nose.tools import *
from nose.tools import assert_raises

try:
    import mongoengine
except ImportError:
    mongoengine = None

def establish_mongo_connection():
    mongo_name = os.environ.get('AASM_MONGO_DB_NAME', 'test_acts_as_state_machine')
    mongo_port = int(os.environ.get('AASM_MONGO_DB_PORT', 27017))
    mongoengine.connect(mongo_name, port=mongo_port)

try:
    import sqlalchemy

    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)
except ImportError:
    sqlalchemy = None

from state_machine import acts_as_state_machine, before, State, Event, after, InvalidStateTransition


def requires_mongoengine(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if mongoengine is None:
            raise SkipTest("mongoengine is not installed")
        return func(*args, **kw)

    return wrapper


def requires_sqlalchemy(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if sqlalchemy is None:
            raise SkipTest("sqlalchemy is not installed")
        return func(*args, **kw)

    return wrapper

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

###################################################################################
## SqlAlchemy Tests
###################################################################################
@requires_sqlalchemy
def test_sqlalchemy_state_machine():
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine()
    class Puppy(Base):
        __tablename__ = 'puppies'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

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


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    puppy = Puppy(name='Ralph')

    eq_(puppy.current_state, Puppy.sleeping)
    assert puppy.is_sleeping
    assert not puppy.is_running
    puppy.run()
    assert puppy.is_running

    session.add(puppy)
    session.commit()

    puppy2 = session.query(Puppy).filter_by(id=puppy.id)[0]

    assert puppy2.is_running


@requires_sqlalchemy
def test_sqlalchemy_named_state_machine():
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine('state')
    class Puppy(Base):
        __tablename__ = 'named_puppies'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

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


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    puppy = Puppy(name='Ralph')

    eq_(puppy.current_state, Puppy.sleeping)
    assert puppy.is_sleeping
    assert not puppy.is_running
    puppy.run()
    assert puppy.is_running

    session.add(puppy)
    session.commit()

    puppy2 = session.query(Puppy).filter_by(id=puppy.id)[0]

    assert puppy2.is_running


@requires_sqlalchemy
def test_sqlalchemy_state_machine_no_callbacks():
    ''' This is to make sure that the state change will still work even if no callbacks are registered.
    '''
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine()
    class Kitten(Base):
        __tablename__ = 'kittens'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    kitten = Kitten(name='Kit-Kat')

    eq_(kitten.current_state, Kitten.sleeping)
    assert kitten.is_sleeping
    assert not kitten.is_running
    kitten.run()
    assert kitten.is_running

    session.add(kitten)
    session.commit()

    kitten2 = session.query(Kitten).filter_by(id=kitten.id)[0]

    assert kitten2.is_running



@requires_sqlalchemy
def test_sqlalchemy_named_state_machine_no_callbacks():
    ''' This is to make sure that the state change will still work even if no callbacks are registered.
    '''
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine('state')
    class Kitten(Base):
        __tablename__ = 'named_kittens'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    kitten = Kitten(name='Kit-Kat')

    eq_(kitten.current_state, Kitten.sleeping)
    assert kitten.is_sleeping
    assert not kitten.is_running
    kitten.run()
    assert kitten.is_running

    session.add(kitten)
    session.commit()

    kitten2 = session.query(Kitten).filter_by(id=kitten.id)[0]

    assert kitten2.is_running


@requires_sqlalchemy
def test_sqlalchemy_state_machine_using_initial_state():
    ''' This is to make sure that the database will save the object with the initial state.
    '''
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine()
    class Penguin(Base):
        __tablename__ = 'penguins'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Note: No state transition occurs between the initial state and when it's saved to the database.
    penguin = Penguin(name='Tux')
    eq_(penguin.current_state, Penguin.sleeping)
    assert penguin.is_sleeping

    session.add(penguin)
    session.commit()

    penguin2 = session.query(Penguin).filter_by(id=penguin.id)[0]

    assert penguin2.is_sleeping



@requires_sqlalchemy
def test_sqlalchemy_named_state_machine_using_initial_state():
    ''' This is to make sure that the database will save the object with the initial state.
    '''
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine('state')
    class Penguin(Base):
        __tablename__ = 'named_penguins'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Note: No state transition occurs between the initial state and when it's saved to the database.
    penguin = Penguin(name='Tux')
    eq_(penguin.current_state, Penguin.sleeping)
    assert penguin.is_sleeping

    session.add(penguin)
    session.commit()

    penguin2 = session.query(Penguin).filter_by(id=penguin.id)[0]

    assert penguin2.is_sleeping


###################################################################################
## Mongo Engine Tests
###################################################################################

@requires_mongoengine
def test_mongoengine_state_machine():

    @acts_as_state_machine()
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

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

    establish_mongo_connection()

    person = Person()
    person.save()
    eq_(person.current_state, Person.sleeping)
    assert person.is_sleeping
    assert not person.is_running
    person.run()
    assert person.is_running
    person.sleep()
    assert person.is_sleeping
    person.run()
    person.save()

    person2 = Person.objects(id=person.id).first()
    assert person2.is_running


@requires_mongoengine
def test_invalid_state_transition():
    @acts_as_state_machine()
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

    establish_mongo_connection()
    person = Person()
    person.save()
    assert person.is_sleeping

    #should raise an invalid state exception
    with assert_raises(InvalidStateTransition):
        person.sleep()


@requires_mongoengine
def test_before_callback_blocking_transition():
    @acts_as_state_machine()
    class Runner(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('run')
        def check_sneakers(self):
            return False

    establish_mongo_connection()
    runner = Runner()
    runner.save()
    assert runner.is_sleeping
    runner.run()
    runner.reload()
    assert runner.is_sleeping
    assert not runner.is_running


if __name__ == "__main__":
    nose.run()
