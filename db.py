import json
import logging


class BotDatabase:
    def __init__(self):
        self._data = {
            "channels": {}
        }

    def load(self, path: str):
        logging.info(f"Loading database from {path}")
        with open(path, "r", encoding="utf-8") as db_file:
            self._data = json.load(db_file)

    def save(self, path: str):
        logging.info(f"Saving database to {path}")
        with open(path, "w", encoding="utf-8") as db_file:
            json.dump(self._data, db_file)

    @property
    def data(self):
        return self._data

    @property
    def channels(self):
        return self._data["channels"]

    def remove_channel(self, channel_id: int):
        assert isinstance(channel_id, int)

        channel_id = str(channel_id)
        
        del self._data["channels"][channel_id]

    def add_emote_filter(self, channel_id: int, regex: str):
        assert isinstance(channel_id, int)
        assert isinstance(regex, str)

        channel_id = str(channel_id)

        if channel_id not in self._data["channels"]:
            self._data["channels"][channel_id] = {
                "emote_filters": [],
                "sent_emotes": [],
            }
        self._data["channels"][channel_id]["emote_filters"].append(regex)

    def remove_emote_filter(self, channel_id: int, regex: str):
        assert isinstance(channel_id, int)
        assert isinstance(regex, str)

        channel_id = str(channel_id)

        if channel_id not in self._data["channels"]:
            logging.warn(f"Channel with id {channel_id} not found")
            return False

        if regex not in self._data["channels"][channel_id]["emote_filters"]:
            logging.warn(f"Emote filter for {regex} not found (filters: {self._data['channels'][channel_id]['emote_filters']})")
            return False

        self._data["channels"][channel_id]["emote_filters"].remove(regex)
        return True