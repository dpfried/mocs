from pylab import *
import matplotlib
colors = {
    0: 0xffffff,
    0.10: 0x99e9fd,
    0.20: 0x00c9fc,
    # 0.30: 0x00e9fd,
    0.30: 0x00a5fc,
    0.40: 0x0078f2,
    0.50: 0x0e53e9,
    0.60: 0x4a2cd9,
    0.70: 0x890bbf,
    0.80: 0x99019a,
    0.90: 0x990664,
    1: 0x660000,
}
offsets = {'red': 16, 'green': 8, 'blue': 0}
cdict = dict((color, tuple((key, (val >> offset & 0xFF) / 256., (val >> offset & 0xFF) / 256.)
                           for key, val in sorted(colors.items())))
             for color, offset in offsets.items())

my_cmap = matplotlib.colors.LinearSegmentedColormap('heatmap', cdict, 256)

if __name__ == "__main__":
    imshow(outer(ones(10), arange(0,1,0.01)), aspect='auto', cmap=my_cmap)
    import matplotlib.pyplot as plt
    plt.axis('off')
    plt.show()
