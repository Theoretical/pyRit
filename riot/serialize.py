import json
from datetime import datetime


class Serialize:
    def toJson(self):
        return json.dumps(self, default=lambda o: str(o) if isinstance(o, datetime) else  o.__dict__, sort_keys=True, indent=4)
