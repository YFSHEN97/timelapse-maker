import numpy as np
import cv2
# import matplotlib.pyplot as plt


class ImageWarper:
    """Warp image using a dense warp field"""

    def __init__(self):
        return

    def warp(self, img, x, y, warp_amount=1):
        # img_warped should be a warped version of img
        # x and y are the warp field in the x and y direction
        # warp amount, if specified, is multiplied by the warp field. So, e.g., warp_amount=0.5 will produce less warping
        img_size = img.shape
        rangex = img_size[1]
        rangey = img_size[0]
        map_y, map_x = np.mgrid[0:rangey, 0:rangex].astype(np.float32)
        map_x += warp_amount * x
        map_y += warp_amount * y

        img_warped = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)

        return img_warped


# if __name__ == "__main__":
#     # Input filename
#     f = './data/test-pattern.png'

#     # Read image
#     img = cv2.imread(f)
#     img_size = img.shape[0:2]

#     # Construct an ImageWarper object
#     w = ImageWarper()

#     # Generate warp field. Values x and y in location (row, col) mean that in the final output, pixel (row, col)
#     # should be sampled from (row, col) + (y, x)
#     warp_field_x = np.full(img_size, 50)
#     warp_field_y = np.full(img_size, 200)
#     # Warp image
#     img_warped = w.warp(img, warp_field_x, warp_field_y)

#     plt.imshow(img_warped[..., ::-1])  # convert from BGR (opencv) to RGB (matplotlib)
#     plt.show()

#     # Note that we specified a constant warp field for all pixels. However, your function must work with
#     # arbitrary warp fields. Add more test cases to make sure everything works as expected.