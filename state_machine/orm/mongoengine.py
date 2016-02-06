from __future__ import absolute_import

try:
    import mongoengine
except ImportError as e:
    mongoengine = None

from state_machine.orm.base import BaseAdaptor


class MongoAdaptor(BaseAdaptor):

    def get_potential_state_machine_attributes(self, clazz):
        # reimplementing inspect.getmembers to swallow ConnectionError
        results = []
        for key in dir(clazz):
            try:
                value = getattr(clazz, key)
            except (AttributeError, mongoengine.ConnectionError):
                continue
            results.append((key, value))
        results.sort()
        return results



    def extra_class_members(self, original_class, state_field_name, initial_state):
        return {state_field_name: mongoengine.StringField(default=initial_state.name), 'id': original_class.pk}

    def update(self, document, state_name):
        setattr(document, document.__class__.state_field_name, state_name)


def get_mongo_adaptor(original_class):
    if mongoengine is not None and issubclass(original_class, mongoengine.Document):
        return MongoAdaptor(original_class)
    return None
