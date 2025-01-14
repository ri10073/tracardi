from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session


class AppendTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'append' not in kwargs and 'remove' not in kwargs:
            raise ValueError("Please define `append` or `remove` in config section.")

        if 'append' in kwargs:
            if not isinstance(kwargs['append'], dict):
                raise ValueError("Please define `append` as dictionary not {}.".format(type(kwargs['append'])))
            self.mapping_append = kwargs['append']
        else:
            self.mapping_append = {}

        if 'remove' in kwargs:
            if not isinstance(kwargs['remove'], dict):
                raise ValueError("Please define 'remove' as dictionary not {}.".format(type(kwargs['remove'])))
            self.mapping_remove = kwargs['remove']
        else:
            self.mapping_remove = {}

    async def run(self, payload: dict):

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for destination, value in self.mapping_append.items():
            value = dot[value]
            if destination in dot:
                if not isinstance(dot[destination], list):
                    # Make it a list with original value
                    dot[destination] = [dot[destination]]

                if value not in dot[destination]:
                    dot[destination].append(value)
            else:
                dot[destination] = value

        for destination, value in self.mapping_remove.items():
            value = dot[value]
            if destination in dot:
                if not isinstance(dot[destination], list):
                    raise ValueError("Can not remove from non-list data.")

                if isinstance(value, list):
                    for v in value:
                        if v in dot[destination]:
                            dot[destination].remove(v)
                elif value in dot[destination]:
                    dot[destination].remove(value)

        if not isinstance(dot.profile['traits']['private'], dict):
            raise ValueError("Error when appending profile@traits.private to value `{}`. "
                             "Private must have key:value pair. "
                             "E.g. `name`: `{}`".format(dot.profile['traits']['private'],
                                                        dot.profile['traits']['private']))

        if not isinstance(dot.profile['traits']['public'], dict):
            raise ValueError(
                "Error when appending profile@traits.public to value `{}`. Public must have key:value pair. "
                "E.g. `name`: `{}`".format(dot.profile['traits']['public'], dot.profile['traits']['public']))

        profile = Profile(**dot.profile)
        event = Event(**dot.event)
        session = Session(**dot.session)

        self.profile.replace(profile)
        self.session.replace(session)
        self.event.replace(event)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.append_trait_action',
            className='AppendTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "append": {
                    "target1": "source1",
                    "target2": "source2",
                },
                "remove": {
                    "target": ["item1", "item2"]
                }
            },
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Append/Remove Trait',
            desc='Appends/Removes trait to/from existing profile trait.',
            type='flowNode',
            width=200,
            height=100,
            icon='append',
            group=["Data processing"]
        )
    )
