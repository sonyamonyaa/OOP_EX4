"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
import math
from Graph.GraphAlgo import GraphAlgo
from Graph.Classes import DiGraph
from client import Client
import json
from pygame import gfxdraw
import pygame
from pygame import *
import pygame_widgets as pw
import pyautogui
import Game
from Game import Agent, Pokemon

# init pygame
WIDTH, HEIGHT = pyautogui.size()

# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'
pygame.init()

screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
clock = pygame.time.Clock()
pygame.font.init()

client = Client()
client.start_connection(HOST, PORT)

button = pw.Button(
    screen, 100, 100,  # coordinates
    300, 150,  # dimensions
    text='stop the game',
    fontSize=50, margin=20,
    inactiveColour=(255, 0, 0),
    pressedColour=(0, 255, 0), radius=20,
    onClick=lambda: client.stop()
)

pokemons = client.get_pokemons()
print(pokemons)

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)

graph = DiGraph()
dga = GraphAlgo(graph)
dga.load_from_json(graph_json)
nodes = dga.get_graph().get_all_v().values()
center = dga.centerPoint().id

# get data proportions
def min_scales():
    minx = math.inf
    miny = math.inf
    for n in nodes:
        if n.pos[0] < minx:
            minx = n.pos[0]
        if n.pos[1] < miny:
            miny = n.pos[1]

    return minx, miny


def max_scales():
    maxx = -math.inf
    maxy = -math.inf
    for n in nodes:
        if n.pos[0] > maxx:
            maxx = n.pos[0]
        if n.pos[1] > maxy:
            maxy = n.pos[1]
    return maxx, maxy


min_x, min_y = min_scales()
max_x, max_y = max_scales()


def scale(data, min_screen, max_screen, min_data, max_data):
    """
    get the scaled data with proportions min_data, max_data
    relative to min and max screen dimentions
    """
    return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen


# decorate scale with the correct values
def my_scale(data, x=False, y=False):
    if x:
        return scale(data, 50, screen.get_width() - 50, min_x, max_x)
    if y:
        return scale(data, 50, screen.get_height() - 50, min_y, max_y)


radius = 15

# add all agents - start point at graph's center
info = json.loads(client.get_info())
agents_amount = info['GameServer']['agents']
for i in range(0, agents_amount):
    client.add_agent("{\"id\":%d}" % center)

# this command starts the server - the game is running now
client.start()

"""
The code below should be improved significantly:
The GUI and the "algo" are mixed - refactoring using MVC design pattern is required.
"""

while client.is_running() == 'true':
    pokemon_json = json.loads(pokemons)
    pokemon_list = Game.load_pokemon(pokemon_json)

    for p in pokemon_list:
        x, y = p.pos
        p.dis_pos = (my_scale(float(x), x=True), my_scale(float(y), y=True))

    agents_json = json.loads(client.get_agents())
    agents_list = Game.load_agents(agents_json)

    for a in agents_list:
        x, y = a.pos
        a.dis_pos = (my_scale(float(x), x=True), my_scale(float(y), y=True))

    # check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client.stop_connection()
            pygame.quit()
            exit(0)

    # refresh surface
    screen.fill(Color(0, 0, 0))

    # draw nodes
    for n in nodes:
        x = my_scale(n.pos[0], x=True)
        y = my_scale(n.pos[1], y=True)

        # its just to get a nice antialias circle
        gfxdraw.filled_circle(screen, int(x), int(y),
                              radius, Color(64, 80, 174))
        gfxdraw.aacircle(screen, int(x), int(y),
                         radius, Color(255, 255, 255))

        # draw the node id
        id_srf = FONT.render(str(n.id), True, Color(255, 255, 255))
        rect = id_srf.get_rect(center=(x, y))
        screen.blit(id_srf, rect)

    # draw edges
    for n in nodes:
        for e in dga.get_graph().all_out_edges_of_node(n):
            # find the edge nodes
            src = dga.get_graph().nodes[n]
            dest = dga.get_graph()

            # scaled positions
            src_x = my_scale(src.pos[0], x=True)
            src_y = my_scale(src.pos[1], y=True)
            dest_x = my_scale(dest.pos[0], x=True)
            dest_y = my_scale(dest.pos[1], y=True)

            # draw the line
            pygame.draw.line(screen, Color(61, 72, 126), (src_x, src_y), (dest_x, dest_y))

    # draw agents
    for agent in agents_list:
        pygame.draw.circle(screen, Color(232, 18, 49),
                           (int(agent.pos.x), int(agent.pos.y)), 10)
    # draw pokemons
    # makes directed triangles, up-facing for 1, down-facing for -1
    for p in pokemon_list:
        r = 10  # triangle 'radius'
        x_p = p.dis_pos[0]
        y_p = p.dis_pos[1]
        if p.type == -1:
            pos = [[x_p, y_p + r], [x_p - r, y_p - r], [x_p + r, y_p - r]]
            pygame.draw.polygon(screen, Color(53, 232, 211), pos)
        elif p.type == 1:
            pos = [[x_p, y_p - r], [x_p - r, y_p + r], [x_p + r, y_p + r]]
            pygame.draw.polygon(screen, Color(232, 165, 32), pos)

    # update screen changes
    display.update()

    # refresh rate
    clock.tick(60)

    # TODO: get src dest edge of a pokemon - e_src e_dest
    # finds the edge a pokemon is placed on, returns the src and dest of that edge
    # assuming for every edge there's am opposite
    def pokemon_src_dest(pokemon):
        edges = dga.get_graph().edges
        # nodes = dga.get_graph().nodes
        py = pokemon.pos[1]
        px = pokemon.pos[0]
        for src in edges.keys():
            for dest in edges[src].keys():
                e_src = dga.get_graph().nodes[src].pos
                e_dest = dga.get_graph().nodes[dest].pos  # idk how to get dest
                sy = e_src[1]
                dy = e_dest[1]
                sx = e_src[0]
                dx = e_dest[0]
                x_within = (sx <= px <= dx) or (sx >= px >= dx)
                y_within = (sy <= py <= dy) or (sy >= py >= dy)
                if x_within and y_within:
                    up_type = pokemon.type == 1
                    bigger_dst = src < dest
                    if (not up_type and not bigger_dst) or (up_type and bigger_dst):
                        return src, dest
                    if (up_type and not bigger_dst) or (not up_type and bigger_dst):
                        return dest, src
        return -1

    # TODO get an agent's travel cost to a pokemon
    def pokemon_cost(pkmn: Pokemon, agnt: Agent):
        cost = -1
        s, d = pokemon_src_dest(pkmn)
        up_type = pkmn.type == 1
        bigger_dst = s < d
        if (not up_type and not bigger_dst) or (up_type and bigger_dst):
                w, rt = dga.shortest_path(agnt.src, s)
                # cost = (w + edge[src][dest]) / pkmn.value

        if (up_type and not bigger_dst) or (not up_type and bigger_dst):
                w, rt = dga.shortest_path(agnt.src, d)
                # cost = (w + edge[dest][src]) / pkmn.value
        return cost


    # choose next edge
    for agent in agents_list:
        if agent.dest == -1:

            min_cost = math.inf
            temp_pokemon = None

            for p in pokemon_list:
                if p.tag == -1:
                    if pokemon_cost(p, agent) < min_cost:
                        min_cost = pokemon_cost(p, agent)
                        temp_pokemon = p

            if temp_pokemon is not None:
                temp_pokemon.tag = 1
                start_e, end_e = pokemon_src_dest(temp_pokemon)

                weight, path = dga.shortest_path(agent.src, start_e)
                path.append(end_e)
                a = 1
                agent.next_node = path[a]

                client.choose_next_edge(
                    '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(agent.next_node) + '}')
                a += 1

                ttl = client.time_to_end()

    if int(ttl) < 30:
        print(client.get_info())

    client.move()
# game over:
