import numpy as np
# import matplotlib.pyplot as plt
from scipy import interpolate

class Extrapolator:
    """Extrapolate and interpolate a sparse vector field into a dense one"""

    def __init__(self):
        return

    # @staticmethod
    # def plot_vector_field(x, y, step=1, scale=1, show_plot=True):
    #     assert x.shape == y.shape
    #     x_loc = np.arange(0, x.shape[1])
    #     y_loc = np.arange(0, x.shape[0])

    #     plt.quiver(x_loc[::step], y_loc[::step], x[::step, ::step], y[::step, ::step], angles='xy', scale_units='xy', scale=1*scale)

    #     if show_plot:
    #         plt.show()

    def extrapolate(self, x, y, z1, z2, out_size):
        # Given two sparse functions f1(x, y) = z1 and f2(x, y) = z2, calculate function values z1_out and z2_out on
        # each point of a regular grid with dimensions out_size

        # add zero-length vectors to boundary (x=0 or x=width-1, y=0 or y=height-1) in the sparse field
        # top edge
        x_padded = np.concatenate((x, np.arange(0, out_size[1])))
        y_padded = np.concatenate((y, np.zeros(out_size[1], dtype=int)))
        z1_padded = np.concatenate((z1, np.zeros(out_size[1], dtype=float)))
        z2_padded = np.concatenate((z2, np.zeros(out_size[1], dtype=float)))
        # left edge
        x_padded = np.concatenate((x_padded, np.zeros(out_size[0]-1, dtype=int)))
        y_padded = np.concatenate((y_padded, np.arange(1, out_size[0])))
        z1_padded = np.concatenate((z1_padded, np.zeros(out_size[0]-1, dtype=float)))
        z2_padded = np.concatenate((z2_padded, np.zeros(out_size[0]-1, dtype=float)))
        # right edge
        x_padded = np.concatenate((x_padded, np.full(out_size[0]-1, out_size[1]-1)))
        y_padded = np.concatenate((y_padded, np.arange(1, out_size[0])))
        z1_padded = np.concatenate((z1_padded, np.zeros(out_size[0]-1, dtype=float)))
        z2_padded = np.concatenate((z2_padded, np.zeros(out_size[0]-1, dtype=float)))
        # bottom edge
        x_padded = np.concatenate((x_padded, np.arange(1, out_size[1]-1)))
        y_padded = np.concatenate((y_padded, np.full(out_size[1]-2, out_size[0]-1)))
        z1_padded = np.concatenate((z1_padded, np.zeros(out_size[1]-2, dtype=float)))
        z2_padded = np.concatenate((z2_padded, np.zeros(out_size[1]-2, dtype=float)))

        # interpolate all points using griddata
        points = np.column_stack((y_padded, x_padded))
        grid_y, grid_x = np.mgrid[0:out_size[0], 0:out_size[1]]
        z1_out = interpolate.griddata(points, z1_padded, (grid_y, grid_x), method="linear")
        z2_out = interpolate.griddata(points, z2_padded, (grid_y, grid_x), method="linear")

        return z1_out, z2_out


# if __name__ == '__main__':
#     img_size = [100, 200]

#     e = Extrapolator()

#     # Generate a random sparse vector field
#     n_samples = 60
#     max_val = 7
#     row = np.random.randint(img_size[0], size=[n_samples])
#     col = np.random.randint(img_size[1], size=[n_samples])
#     data_x = np.random.rand(n_samples) * max_val - (max_val / 2)
#     data_y = np.random.rand(n_samples) * max_val - (max_val / 2)

#     # Plot the sparse vector field
#     x_orig = np.full(img_size, np.nan)
#     y_orig = np.full(img_size, np.nan)
#     x_orig[row, col] = data_x
#     y_orig[row, col] = data_y
#     fig = plt.figure(figsize=(20, 10))
#     plt.subplot(1, 2, 1)
#     plt.title('Sparse vector field')
#     e.plot_vector_field(x_orig, y_orig, show_plot=False)

#     # Generate a dense vector field from the sparse one
#     x, y = e.extrapolate(col, row, data_x, data_y, img_size)

#     # Plot the dense vector field
#     plt.subplot(1, 2, 2)
#     plt.title('Dense vector field')
#     e.plot_vector_field(x, y, step=5)

#     # You might want to add more test cases with non-random data, to make sure everything works as expected
