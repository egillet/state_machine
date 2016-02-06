from __future__ import absolute_import

try:
    import sqlalchemy
    from sqlalchemy import inspection
    from sqlalchemy.orm import instrumentation
    from sqlalchemy.orm import Session
except ImportError:
    sqlalchemy = None
    instrumentation = None

from state_machine.orm.base import BaseAdaptor


class SqlAlchemyAdaptor(BaseAdaptor):
    def extra_class_members(self, original_class, state_field_name, initial_state):
        return {state_field_name: sqlalchemy.Column(sqlalchemy.String)}

    def update(self, document, state_name):
        setattr(document, document.__class__.state_field_name, state_name)

    def modifed_class(self, original_class, callback_cache, state_field_name):
        class_dict = dict()

        class_dict['callback_cache'] = callback_cache

        def current_state_method():
            def f(self):
                return getattr(self, self.__class__.state_field_name)

            return property(f)

        class_dict['current_state'] = current_state_method()

        # Get states
        class_dict['state_field_name'] = state_field_name
        state_method_dict, initial_state = self.process_states(original_class)
        class_dict.update(self.extra_class_members(original_class, state_field_name, initial_state))
        class_dict.update(state_method_dict)

        orig_init = original_class.__init__

        def new_init(self, *args, **kwargs):
            orig_init(self, *args, **kwargs)
            setattr(self, self.__class__.state_field_name, initial_state.name)

        class_dict['__init__'] = new_init

        # Get events
        event_method_dict = self.process_events(original_class)
        class_dict.update(event_method_dict)

        for key in class_dict:
            setattr(original_class, key, class_dict[key])

        return original_class


def get_sqlalchemy_adaptor(original_class):
    if sqlalchemy is not None and hasattr(original_class, '_sa_class_manager') and isinstance(
            original_class._sa_class_manager, instrumentation.ClassManager):
        return SqlAlchemyAdaptor(original_class)
    return None
