import time, random

class Network():
    def __init__(self, image_width: int, image_height: int, stack_count: int):
        self.stacks = []

        for i in range(stack_count):
            self.stacks.append(Stack(image_width, image_height))
        
    def output(self, image: list):
        new_image = self.stacks[0].output(image)

        for i in range(1, len(self.stacks)):
            new_image = self.stacks[i].output(new_image)
            
        return new_image
    
class Stack():
    def __init__(self, image_width: int, image_height: int):
        self.layers = []
        
        for i in range(image_height):
            self.layers.append(Layer(image_width))
        
    def output(self, rows: list):
        results = []
        
        for y in range(len(rows)):
            results.append(self.layers[y].output(rows[y]))
            
        return results

class Layer():
    def __init__(self, neuron_count: int):
        self.neurons = []
        
        for n in range(neuron_count):
            self.neurons.append(Neuron([random.randrange(0, 2), random.randrange(0, 2), random.randrange(0, 2)], random.random()))
        
    def output(self, columns: list):
        results = []

        for x in range(len(columns)):
            results.append(self.neurons[x].output(columns[x]))
            
        return results

class Neuron():
    def __init__(self, weights: list, bias: int):
        self.weights = weights
        self.bias = bias

    def output(self, colors: list):
        results = []

        for c in range(len(colors)):
            result = self.weights[c] * colors[c] + self.bias
            
            #clamp 0 to 1
            if result < 0:
                result = 0
            elif result > 1:
                result = 1
                
            results.append(round(result, 2))
            
        return results

#Create random sample image
height = 120
width = 160
depth = 4

sample_image = []
for y in range(height):
    columns = []
    
    for x in range(width):
        color = [random.randrange(0, 2), random.randrange(0, 2), random.randrange(0, 2)]
        columns.append(color)

    sample_image.append(columns)

#Init network
start_time = time.perf_counter_ns()    
network = Network(width, height, depth)
print("\n[Network Init Finished in " + str((time.perf_counter_ns() - start_time) / 1000000) + " milliseconds]\n")

#Generate output image
step_time = time.perf_counter_ns()
print("Output: " + str(network.output(sample_image)))
print("\n[Output generated in " + str((time.perf_counter_ns() - step_time) / 1000000) + " milliseconds]\n")
print("\n[Finished in " + str((time.perf_counter_ns() - start_time) / 1000000) + " milliseconds]\n")