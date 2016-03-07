from __future__ import absolute_import
import inspect
from state_machine.models import Event, State, InvalidStateTransition


class BaseAdaptor(object):

    def __init__(self, original_class):
        self.original_class = original_class

    def get_potential_state_machine_attributes(self, clazz):
        results = []
        for key in dir(clazz):
            try:
                value = getattr(clazz, key)
            except AttributeError:
                continue
            results.append((key, value))
        return results

    def process_states(self, original_class):
        initial_state = None
        for member, value in self.get_potential_state_machine_attributes(original_class):
            if isinstance(value, State):
                if value.initial:
                    if initial_state is not None:
                        raise ValueError("multiple initial states!")
                    initial_state = value
                #add its name to itself:
                setattr(value, 'name', member)

                is_method_string = "is_" + member
                def is_method_builder(member):
                    def f(self):
                        return getattr(self, self.__class__.state_field_name) == str(member)
                    return property(f)

                setattr(original_class, is_method_string, is_method_builder(member))
        return initial_state

    def process_events(self, original_class):
        _adaptor = self
        for member, value in self.get_potential_state_machine_attributes(original_class):
            if isinstance(value, Event):
                # Create event methods
                def event_meta_method(event_name, event_description):
                    def f(self, *args, **kwargs):
                        #assert current state
                        if self.current_state not in event_description.from_states:
                            raise InvalidStateTransition
                        # fire before_change
                        failed = False
                        if self.__class__.callback_cache and \
                                event_name in self.__class__.callback_cache[_adaptor.original_class.__name__]['before']:
                            for callback in self.__class__.callback_cache[_adaptor.original_class.__name__]['before'][event_name]:
                                result = callback(self, *args, **kwargs)
                                if result is False:
                                    failed = True
                                    break
                        #change state
                        if failed:
                            return False
                        else:
                            setattr(self, self.__class__.state_field_name, event_description.to_state.name)
                          
                            #fire after_change
                            if self.__class__.callback_cache and \
                                    event_name in self.__class__.callback_cache[_adaptor.original_class.__name__]['after']:
                                for callback in self.__class__.callback_cache[_adaptor.original_class.__name__]['after'][event_name]:
                                    callback(self, *args, **kwargs)
                            return True
                    return f
                    
                setattr(original_class, member, event_meta_method(member, value))

    def modifed_class(self, original_class, callback_cache, state_field_name):
        setattr(original_class, 'callback_cache', callback_cache)

        def current_state_method():
            def f(self):
                return getattr(self, self.__class__.state_field_name)
            return property(f)
        setattr(original_class, 'current_state', current_state_method())

        # Get states
        setattr(original_class, 'state_field_name', state_field_name)
        initial_state = self.process_states(original_class)
        if not state_field_name in original_class.__dict__:
          setattr(original_class, state_field_name, initial_state.name)

        # Get events
        self.process_events(original_class)
