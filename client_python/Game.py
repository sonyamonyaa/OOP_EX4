class Agent:

    def __init__(self, id: int, value: float, src: int, dest: int, speed: float, pos: tuple):
        self.id = id
        self.value = value
        self.src = src
        self.dest = dest
        self.speed = speed
        self.pos = pos
        self.dis_pos = pos  # display position
        self.next_node = src
        self.path = []
        self.current_path = 0
        self.tag = -1

    def __str__(self):
        return f"{self.id},{self.value},{self.speed},{self.pos}"

    def __repr__(self):
        return f"{self.id},{self.value},{self.speed},{self.pos}"


class Pokemon:

    def __init__(self, value: float, type: int, pos: tuple):
        self.value = value
        self.type = type
        self.pos = pos
        self.tag = -1
        self.dis_pos = pos  # display position

    def __str__(self):
        return f"{self.value},{self.type},{self.pos},{self.tag}"

    def __repr__(self):
        return f"{self.value},{self.type},{self.pos},{self.tag}"


def load_agents(json_dict: dict):
    temp_list = []

    for d in json_dict['Agents']:
        pos = (d['Agent']['pos'].split(","))
        a = Agent(d['Agent']['id'], d['Agent']['value'], d['Agent']['src'], d['Agent']['dest'], d['Agent']['speed'],
                  (float(pos[0]), float(pos[1])))
        temp_list.append(a)
    return temp_list


def load_pokemon(json_dict: dict):
    temp_list = []
    # poke_id = 0
    for d in json_dict['Pokemons']:
        pos = (d['Pokemon']['pos'].split(","))
        p = Pokemon(d['Pokemon']['value'], d['Pokemon']['type'], (float(pos[0]), float(pos[1])))
        # poke_id += 1
        temp_list.append(p)
    return temp_list
