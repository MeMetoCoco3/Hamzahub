import json


class Location:
    with open(r".config\config_database.json", "r") as f:
        warehouse_information = json.load(f)["WAREHOUSE_DIMENSIONS"]

    total_locations = 0
    num_locations = 0
    for _, v in warehouse_information.items():
        total_locations += v["Rows"] * len(v["Levels"])

    def __init__(self, aisle, row=None, level=None, state="E", digi=None):
        if Location.num_locations < Location.total_locations and digi == None:
            self.id = Location.num_locations
            Location.num_locations += 1
            self.aisle = aisle
            self.row = row
            self.level = level
            self.state = state

        # When digi, the number of location will not go up.
        elif digi == "digi":
            self.id = None
            self.aisle = aisle
            self.row = row
            self.level = level
            self.state = state

        else:
            raise ValueError("Not Enough Locations")

    def __str__(self):
        return f"Type of Pallet: {self.aisle} Company: {self.row} Number of boxes: {self.level}"

    @classmethod
    def get_id(cls):
        return cls.id

    @property
    def aisle(self):
        return self._aisle

    @aisle.setter
    def aisle(self, aisle):
        location_info = Location.warehouse_information[aisle]

        self._aisle = aisle
        self._total_rows = location_info["Rows"]
        self._ADR = location_info["ADR"]
        self._levels = location_info["Levels"]

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        if value == None:
            self._row = value
        elif value > self._total_rows or value < 0:
            raise ValueError("This position does not exist")
        else:
            self._row = value

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level == None:
            pass
        elif level.strip() not in self._levels:
            raise ValueError(f"Level: '{level}' not in range")
        else:
            try:
                location_info = Location.warehouse_information[self.aisle]["Levels"]
            except KeyError:
                print("Aisle is not in config_database.json")
            else:
                self._level = level
                self.max_height = location_info[level]["Height"]
                self.max_weight = location_info[level]["Weight"]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        states = ["E", "F"]
        if state in states:
            self._state = state
        else:
            raise ValueError("Not correct state")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    def encoder_warehouse(self) -> dict:
        d_loc = {f"{self.aisle}/{self.row}/{self.level}": self.state}
        return d_loc


def get_id(loc):
    try:
        check = loc.split("/")
        if len(check) != 3:
            raise ValueError
        a, pos, lev = loc.split("/")
        pos = int(pos)

        aisles = list(Location.warehouse_information.keys())
        aisle_index = aisles.index(a)
    except ValueError:
        print("Wrong ID Code")
        return "ERROR"
    else:
        id = 0
        values = Location.warehouse_information
        for i in aisles[:aisle_index]:
            id += values[i]["Rows"] * len(values[i]["Levels"])
        id += (
            pos
            + (len(values[a]["Levels"]) - 1) * (pos - 1)
            + list(values[a]["Levels"]).index(lev)
        )
        return id


def get_loc_from_loc_code(loc_code) -> Location:
    # Checks dict and str
    if isinstance(loc_code, dict):
        a, b, c = list(loc_code.keys())[0].split("/")
        return Location(a, int(b), c.strip(), state="E", digi="digi")
    elif isinstance(loc_code, str):
        a, b, c = loc_code.split("/")
        return Location(a, int(b), c.strip(), state="E", digi="digi")


def increase_hex(hex_num: str, increment: int) -> str:
    if len(hex_num) == 0 or len(hex_num) > 8:
        raise KeyError
    if hex_num[0] == '#':
        hex_num = hex_num[1:]

    hsl = rgbToHsl(hex_num)
    hsl[2] += increment
    if hsl[2] < 0:
        hsl[2] == 0

    return hslToRgb(hsl)


def rgbToHsl(hex_num:str)->list[int]:
    if len(hex_num) > 7 or len(hex_num) < 6:
        raise KeyError
    if hex_num[0] == '#':
        hex_num = hex_num[1:]

    r = int(hex_num[ :2], 16)/255
    g = int(hex_num[2:4], 16)/255
    b = int(hex_num[4: ], 16)/255
    cmax = max([r,g,b])
    cmin = min([r,g,b])
    
    delta = cmax - cmin
    lightness = (cmax+cmin)/2

    if delta == 0:
        saturation = 0
    else:
        saturation = delta/(1-abs((2*lightness-1)))

    if delta == 0:
        hue = 0
    elif cmax == r:
        hue = (60 * ((g - b) / delta) + 360) % 360
    elif cmax == g:
        hue = (60 * ((b - r) / delta) + 120) % 360
    elif cmax ==  b:
        hue = (60 * ((r - g) / delta) + 240) % 360
    
    return [round(hue), round(saturation*100), round(lightness*100)]

def hslToRgb(hsl: list[int])->str:
    h,s,l = hsl
    h /= 60
    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs(h % 2 - 1))
    m = l - c / 2

    if 0 <= h < 1:
        r, g, b = c, x, 0
    elif 1 <= h < 2:
        r, g, b = x, c, 0
    elif 2 <= h < 3:
        r, g, b = 0, c, x
    elif 3 <= h < 4:
        r, g, b = 0, x, c
    elif 4 <= h < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x


    re = round((r + m) * 255)
    gr = round((g + m) * 255)
    bl = round((b + m) * 255)

    if re>255: re = 255
    if gr>255: gr = 255
    if bl>255: bl = 255

    if re<0: re = 0
    if gr<0: gr = 0
    if bl<0: bl = 0

    re = hex(re)[2:].zfill(2)
    gr = hex(gr)[2:].zfill(2)
    bl = hex(bl)[2:].zfill(2)

    return f"#{re}{gr}{bl}"