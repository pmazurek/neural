import random
import copy
import string


class Neuron:

    def __init__(self, threshold=None):
        self.connections = []
        self.saturation = 0
        if threshold == None:
            self.threshold = 0.5
        else:
            self.threshold = threshold

        chars = [x for x in string.ascii_lowercase]
        random.shuffle(chars)
        self.name = ''.join(chars[0:3])

    def fire(self):
        for connection in self.connections:
            connection.propagate(self)

    def receive_fire(self, connection):
        self.saturation += connection.strength
        if self.saturation >= self.threshold:
            self.fire()

    def make_connection(self, strength, other_neuron):
        self.connections.append(
            Connection(strength, self, other_neuron)
        )

    def clean_saturation(self):
        self.saturation = 0

    def __repr__(self):
        output = []
        output.append("Name: %s" % self.name)
        output.append("Threshold: %s" % str(self.threshold)) 
        output.append("Saturation: %s" % str(self.saturation)) 
        output.append("Connections:")

        for connection in self.connections:
            output.append("%s -> %s -> %s" % (connection.neuronA.name, connection.strength, connection.neuronB.name))
        output.append("")
        return "\n".join(output)


class Connection:

    def __init__(self, strength, neuronA, neuronB):
        self.strength = strength
        self.neuronA = neuronA
        self.neuronB = neuronB
    
    def propagate(self, fired_neuron):
        if fired_neuron == self.neuronA:
            self.neuronB.receive_fire(self)
        else:
            self.neuronA.receive_fire(self)


class Network:

    def __init__(self, input_neurons, hidden_layers_count, hidden_neuron_count, output_neurons):
        self.input_layer = []
        self.hidden_layers = []
        self.output_layer = []

        # create input layer
        for x in range(0, input_neurons):
            self.input_layer.append(Neuron())

        # create middle layers and add backwards connection
        previous_layer = False
        for layer in range(0, hidden_layers_count):
            hidden_layer = []
            for neuron in range(0, int(hidden_neuron_count/hidden_layers_count)):
                hidden_layer.append(Neuron())
            self.hidden_layers.append(hidden_layer)
            if previous_layer:
                for previous_neuron in previous_layer:
                    for current_neuron in hidden_layer:
                        previous_neuron.make_connection(random.random(), current_neuron)
            else:
                for input_neuron in self.input_layer:
                    for current_neuron in hidden_layer:
                        input_neuron.make_connection(random.random(), current_neuron)

            previous_layer = hidden_layer

        # create output layer
        for x in range(0, output_neurons):
            self.output_layer.append(Neuron())

        # create connections to the last hidden layer
        for previous_neuron in previous_layer:
            for current_neuron in self.output_layer:
                previous_neuron.make_connection(random.random(), current_neuron)

        self.all_neurons = []

        self.all_neurons.extend(self.input_layer)
        for layer in self.hidden_layers:
            self.all_neurons.extend(layer)

        self.all_neurons.extend(self.output_layer)

    def randomize_connections(self):
        for neuron in self.all_neurons:
            for connection in neuron.connections:
                connection.strength = connection.strength + random.uniform(-0.1, 0.1)

    def reset(self):
        for neuron in self.all_neurons:
            neuron.clean_saturation()


# Assumptions:
# 1, 0 -> 1, 0, 0
# 0, 1 -> 0, 1, 0
# 1, 1 -> 0, 0, 1


# initiate the networks
networks = []
for x in range(0, 500):
    networks.append(Network(2, 4, 40, 3))


def compute_network(network):
    desired_effects = [
        ((1, 0), (10, 5, 5)),
        ((0, 1), (5, 10, 5)),
        ((1, 1), (5, 5, 10)),
    ]
    print(' ============ NETWORK ============= ')

    score = 0
    for desired_effect in desired_effects:
        inputs_config = desired_effect[0]
        desired_outputs = desired_effect[1]
        print("Input: %s" % str(inputs_config))
        print("Desired effect: %s" % str(desired_effect))

        # Fire all the inputs in desired input
        for (input_number, is_fired) in enumerate(inputs_config):
            if is_fired:
                network.input_layer[input_number].fire()

        # check outputs and judge how far away from score
        for (output_number, desired_value) in enumerate(desired_outputs):
            score_distance = abs(network.output_layer[output_number].saturation - desired_value)

            print("Score distance for output nr %s, value: %s, desired val: %s, score: %s" % (output_number, network.output_layer[output_number].saturation, desired_value, score_distance))
            # sum up the score (smaller distance is better)
            score += score_distance


        network.reset()

    return score

import concurrent.futures

# repeat the process for X generations
for generation in range(1, 10000):

    print("Generation %s " % generation) 

    ## judge networks by assumptions
    scores = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for network, score in zip(networks, executor.map(compute_network, networks)):
            print("Score %s" % score)
            scores.append((score, network))


#        for network in networks:
#            score = compute_network(network, desired_effects)
#            # save the score of the network
#            print("Score %s" % score)
#            scores.append((score, network))
#                

    # order the networks according to the score
    # take 5 top networks and create 10 more with deepcopy (5 each)
    top_net = sorted(scores, key=lambda x: x[0])[0:4]
    new_networks = []
    for top_network in top_net:
        for x in range(0, 4):
            new_networks.append(copy.deepcopy(top_network[1]))


    for network in new_networks:
        network.randomize_connections()


    new_networks.append(top_net[0][1]) # append best network
    #random.shuffle(new_networks)

    networks = new_networks


import pdb; pdb.set_trace()

