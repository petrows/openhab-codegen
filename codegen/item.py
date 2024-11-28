from ast import Str
from typing import List

class Item:
    def __init__(self) -> None:
        self.conf_str = list()
        self.gen_sitemap_items_str = list()
        pass

    def get_config(self) -> List[Str]:
        """
            Return strings list to place in 'gen.items'
        """
        return self.conf_str

    def get_sitemap_config(self) -> List[Str]:
        """
            Return strings to place in 'gen.sitemap'
        """
        return self.gen_sitemap_items_str

class Generic_Item(Item):
    def __init__(self,
        id: Str,
        name: Str,
        type: Str,
        icon: Str = None,
        groups: List[str] = list(),
    ) -> None:
        Item.__init__(self)
        item_conf = list()

        item_conf.append(type)
        item_conf.append(id)
        item_conf.append(f"\"{name}\"")
        if icon:
            item_conf.append(f"<{icon}>")
        if groups:
            item_conf.append("(" + ",".join(groups) + ")")

        self.conf_str.append(" ".join(item_conf))

class MQTT_Item(Item):
    def __init__(self,
        id: Str,
        name: Str,
        type: Str,
        broker: Str,
        channel_id: Str,
        groups: List[str] = list(),
        expire: Str = None,
        sitemap_type: Str = None,
        icon: Str = None,
    ) -> None:
        Item.__init__(self)
        item_conf = list()

        item_conf.append(type)
        item_conf.append(id)
        item_conf.append(f"\"{name}\"")
        if icon:
            item_conf.append(f"<{icon}>")
        if groups:
            item_conf.append("(" + ",".join(groups) + ")")

        item_channel = list()
        item_channel.append(f"channel=\"mqtt:topic:{broker}:{channel_id}\"")

        if expire:
            item_channel.append(f"expire=\"{expire}\" [ignoreStateUpdates=\"true\"]")
        item_conf.append("{" + ", ".join(item_channel) + "}")

        self.conf_str.append(" ".join(item_conf))

        if sitemap_type:
            self.gen_sitemap_items_str.append(
                f"{sitemap_type} item={id}"
            )
