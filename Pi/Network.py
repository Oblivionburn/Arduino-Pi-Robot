import time, random

"""
This is an unsupervised self-training model built for predicting the next frame
    in a continual video feed.
    
The intended usage and training process:
    1. Input a frame/image of video
    2. Output a new image, which we'll refer to as "oFrame" for this explanation
    3. The next frame of the video (which we'll refer to as "vFrame") is then used
        as the accuracy test
    4. If oFrame does not match vFrame, backpropagate vFrame to tune the model
    5. vFrame becomes the new input for Step #1 to repeat cycle of training
    
Because this is intended to be used real-time for a continual video feed,
    speed/performance is paramount for this to keep up with the rate of the feed.
    Tolerable lowest rate of video feed is usually 29 frames per second, so the
    entire process needs to run within 34.48 milliseconds to maintain 29fps.
"""

class Network():
    #Initialize network with width/height of the video feed
    #This width/height will become a constant for the model
    #DO NOT try to re-use this model with a different width/height after it's been initialized
    
    def __init__(self, image_width: int, image_height: int, layer_count: int):
        self.learning_rate = 0.01
        self.layers = []

        for s in range(layer_count):
            self.layers.append(Layer(s, image_width, image_height))
        
    def forward(self, image: list):
        #Feed image to first layer to get output
        new_image = self.layers[0].forward(image)

        #Output of every layer becomes input of next layer
        for i in range(0, len(self.layers)):
            new_image = self.layers[i].forward(new_image)
            
        #Return final output
        return new_image
    
    def backward(self, predicted_image: list, true_image: list, learning_rate: float):
        deltas = self.layers[len(self.layers) - 1].backward(predicted_image, true_image, learning_rate)
        
        for i in range(len(self.layers) - 2, -1, -1):
            deltas = self.layers[i].backward(predicted_image, true_image, learning_rate, deltas)
    
class Layer():
    def __init__(self, image_width: int, image_height: int):
        self.rows = []
        
        for i in range(image_height):
            self.rows.append(Row(image_width))
        
    def forward(self, rows: list):
        results = []
        
        for y in range(len(rows)):
            results.append(self.rows[y].forward(rows[y]))
            
        return results
    
    def backward(self, predicted_rows: list, true_rows: list, learning_rate: float, lower_delta_rows: list):
        deltas = []
        
        if (len(lower_delta_rows) > 0):
            for y in range(len(predicted_rows)):
                deltas.append(self.rows[y].backward(predicted_rows[y], true_rows[y], learning_rate, lower_delta_rows[y]))
        else:
            for y in range(len(predicted_rows)):
                deltas.append(self.rows[y].backward(predicted_rows[y], true_rows[y], learning_rate))
            
        return deltas

class Row():
    def __init__(self, width: int):
        self.columns = []
        
        #Gen random list of [[R, G, B], bias]
        for n in range(width):
            self.columns.append(Column([random.randrange(0, 2), random.randrange(0, 2), random.randrange(0, 2)], random.random()))
        
    def forward(self, columns: list):
        results = []

        for x in range(len(columns)):
            results.append(self.columns[x].forward(columns[x]))
            
        return results
    
    def backward(self, predicted_columns: list, true_columns: list, learning_rate: float, lower_delta_columns: list):
        deltas = []
        
        if (len(lower_delta_columns) > 0):
            for x in range(len(predicted_columns)):
                deltas.append(self.columns[x].backward(predicted_columns[x], true_columns[x], learning_rate, lower_delta_columns[x]))
        else:
            for x in range(len(predicted_columns)):
                deltas.append(self.columns[x].backward(predicted_columns[x], true_columns[x], learning_rate))

        return deltas

class Column():
    def __init__(self, color: list, bias: int):
        self.color = color #[R, G, B] as weights
        self.bias = bias

    def forward(self, color: list):
        results = []

        for i in range(len(color)):
            result = self.color[i] * color[i] + self.bias
            
            #clamp new color result as 0 to 1
            if result < 0:
                result = 0
            elif result > 1:
                result = 1
                
            results.append(round(result, 2))
            
        return results
    
    def backward(self, predicted_color: list, true_color: list, learning_rate: float, lower_delta_colors: float):
        delta_sum = 0
        
        if lower_delta_colors is not None:
            for i in range(len(predicted_color)):
                delta = self.color[i] * lower_delta_colors
                gradient = delta * learning_rate
                
                self.color[i] -= gradient
                self.bias -= gradient
                
                delta_sum += delta
        else:
            for i in range(len(predicted_color)):
                error = true_color[i] - predicted_color[i]
                derivative = predicted_color[i] * (1 - predicted_color[i])
                delta = error * derivative
                gradient = delta * learning_rate
                
                self.color[i] -= gradient
                self.bias -= gradient

                delta_sum += delta
            
        #Return average color delta
        return delta_sum / 3

#Network parameters
height = 12
width = 16
layers = 6

#Randomly generated image for testing output speed
sample_image = []
for y in range(height):
    columns = []
    
    for x in range(width):
        color = [random.randrange(0, 2), random.randrange(0, 2), random.randrange(0, 2)]
        columns.append(color)

    sample_image.append(columns)

#Init network
start_time = time.perf_counter_ns()    
network = Network(width, height, layers)
print("\n[Network Init Finished in " + str((time.perf_counter_ns() - start_time) / 1000000) + " milliseconds]\n")

#Generate output image
output_time = time.perf_counter_ns()
print("Output: " + str(network.forward(sample_image)))
print("\n[Output generated in " + str((time.perf_counter_ns() - output_time) / 1000000) + " milliseconds]\n")

total_time = time.perf_counter_ns() - start_time
print("\n[Finished in " + str(total_time / 1000000) + " milliseconds]\n")