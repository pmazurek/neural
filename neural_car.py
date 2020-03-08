import pickle

from physics_2d import *
from neural_net import Network


track = load_track_data_from_image('tracks/1.png')

# generate networks
networks = []
for _ in range(0, 16):
    networks.append(
        Network(5, 3, 15, 2)
    )

def compute_network(network):
    plane = PhysicalPlaneWithTrack(track)
    sim = Simulation(plane)
    car = Car(
        10, 20, 200,
        CarNeuralControlManager(network)
    )
    plane.add_physical_object(car, position=Vector2D(2, 4))

    collision, last_step = sim.simulate()
    print(collision, last_step)
    # calculate how far away from end of track
    final_position = plane.physical_objects[0][1]
    score = (500 - final_position.x) + (500 - final_position.y)
    return score

import concurrent.futures

for generation in range(0, 1000):
    scored_networks = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for network, score in zip(networks, executor.map(compute_network, networks)):
            score = compute_network(network)
            scored_networks.append((score, network))

    # order by highest score
    top_networks = sorted(scored_networks, key=lambda x: x[0])[0:5]
    for net in top_networks:
        print(net[0])
    new_networks = []

    for top_network in top_networks:
        for x in range(0, 3):
            new_networks.append(
                copy.deepcopy(top_network[1])
            )

    for network in new_networks:
        network.randomize_connections()
        
    new_networks.append(top_networks[0][1]) # append best network
    new_networks.append(top_networks[1][1]) # append best network
    new_networks.append(top_networks[2][1]) # append best network

    networks = new_networks
        

pickle.dump(sim, open("result.sim", "wb"))
