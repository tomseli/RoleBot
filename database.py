import json


class Data:
    def __init__(self, id: int, roleless_id: int, role_id: int) -> None:
        self.server_id = id
        self.roleless_id = roleless_id
        self.role_id = role_id

    def __str__(self):
        return f"DataObject({self.server_id}, {self.roleless_id}, {self.role_id})"

class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self.data = self.load_data()

    def get(self) -> list[Data]:
        return self.data

    def add(self, d: Data) -> None:
        if d not in self.data:
            self.data.append(d)

    def pop(self, d: Data) -> list[Data]:
        new = []
        for x in self.data:
            if x == d:
                continue 
            new.append(x)
        self.data = new
        return self.data

    def serialize_data(self) -> None:
        res = [vars(x) for x in self.data]
        with open(self.path, "w+") as file:
            json.dump(res, file)
        return None

    def load_data(self) -> list[Data]:
        dicts = []
        try:
            with open(self.path, "r") as file:
                dicts = json.load(file)
        except FileNotFoundError:
            with open(self.path, "w+") as file:
                file.write("[]")
        self.data = [Data(x["server_id"], x["roleless_id"], x["role_id"]) for x in dicts]
        return self.data


if __name__ == "__main__":
    data = Data(69, 80085, 420)
    db = Database("data.json")
    print(db.data)
    # db.serialize_data([data])
