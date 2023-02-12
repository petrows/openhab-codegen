from ast import Str
from typing import List

class Thing:
    def __init__(self):
        self.conf_str = list()

    def get_config(self) -> List[Str]:
        return self.conf_str


class MQTT_ThingChannel:
    def __init__(
            self,
            type: Str,
            id: Str,
            args,
        ) -> None:
        args_str = list()
        for k, v in args.items():
            if isinstance(v, str):
                v = v.translate(str.maketrans({'"': '\\"'}))
                v = f'"{v}"'
            args_str.append(f'{k}={v}')
        config = f"\t\tType {type} : {id} [{', '.join(args_str)}]"
        self.conf_str = [config]

    def get_config(self) -> List[Str]:
        return self.conf_str

class MQTT_Thing(Thing):
    def __init__(
        self,
        id: Str,
        name: Str,
        broker: Str,
        channels: List[MQTT_ThingChannel],
    ) -> None:
        Thing.__init__(self)
        self.conf_str.append(
            f"Thing mqtt:topic:{broker}:{id} \"{name}\" (mqtt:broker:{broker}) {{")
        self.conf_str.append(
            f"\tChannels:")
        for channel in channels:
            self.conf_str.extend(channel.get_config())
        self.conf_str.append(f"}}")

