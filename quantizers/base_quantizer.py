import torch
from compressors import IdenticalCompressor

class Quantizer():
    def __init__(self, Compressor, parameters, args):
        self.parameters = list(parameters)
        self.num_layers = len(self.parameters)
        self.compressors = list()
        self.compressed_gradients = [list() for _ in range(self.num_layers)]
        for param in self.parameters:
            param_size = param.flatten().shape[0]
            self.compressors.append(
                Compressor(param_size, param.shape, args) if param_size > 1000
                else IdenticalCompressor()
            )

    def record(self):
        for i, param in enumerate(self.parameters):
            self.compressed_gradients[i].append(
                self.compressors[i].compress(param.grad.data))

    def apply(self):
        for i, param in enumerate(self.parameters):
            decompressed_gradients = [self.compressors[i].decompress(
                compressed) for compressed in self.compressed_gradients[i]]
            param.grad.data = torch.stack(decompressed_gradients, dim=0).mean(dim=0)
        for compressed in self.compressed_gradients:
            compressed.clear()
