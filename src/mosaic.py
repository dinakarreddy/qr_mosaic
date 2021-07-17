import numpy as np
import os
import random
from PIL import Image
from cachetools import Cache


def get_tile_split_masks(split_len, data):
    data_dict = {}
    qr_len = len(data)
    n = int(qr_len / split_len)
    for i in range(split_len):
        for j in range(split_len):
            i_end_index = (i + 1) * n
            j_end_index = (j + 1) * n
            if i == split_len - 1:
                i_end_index = None
            if j == split_len - 1:
                j_end_index = None
            data_dict[(i, j)] = np.copy(data[i * n:i_end_index, j * n:j_end_index])
    return data_dict


def get_tile_split_img_dict(cache, file_index, tile_file_names, tile_size, tile_to_user_img_pixel_ratio):
    tile_split_img_dict = cache.get(file_index)
    if tile_split_img_dict is not None:
        return tile_split_img_dict
    print("Img data not present in cache, loading it")
    file_name = tile_file_names[file_index]
    tile_data = np.array(Image.open(file_name).convert('RGB').resize((tile_size, tile_size)))
    tile_split_data_dict = get_tile_split_masks(tile_to_user_img_pixel_ratio, tile_data)
    tile_split_img_dict = {index: Image.fromarray(value) for index, value in tile_split_data_dict.items()}
    cache[file_index] = tile_split_img_dict
    return tile_split_img_dict


def main(img_file_path='images/1.jpeg', final_img_file_path='images/result_images/mosaic.jpeg',
         tile_directory='images/image_set', tile_size=2000, tile_to_user_img_pixel_ratio=100, user_img_len=1000,
         user_img_breadth=1000, cache_size=10):
    """
    :param img_file_path: The image that needs to be made as a mosaic
    :param final_img_file_path: Final mosaic image will be stored at this path
    :param tile_directory: The directory from which images are picked up to make part of mosaic image
    :param tile_size: Size in pixels of each tile in the final mosaic image
    :param tile_to_user_img_pixel_ratio: This will decide the number of sub images inside the mosaic
    :param user_img_len: The image that needs to be made as a mosaic will be resized to this
    :param user_img_breadth: The image that needs to be made as a mosaic will be resized to this
    :param cache_size: Number of images stored in memory. Depending on the RAM of the machine need to control this

    The function creates a mosaic image at final_img_file_path
    The final image will contain the following number of sub images:
        (user_img_len/tile_to_user_img_pixel_ratio) * (user_img_breadth/tile_to_user_img_pixel_ratio)
    tile_size decides the number of pixels each sub image will contain, so this will decide the clarity of each image.
        Higher the number, higher the quality with the downside being increased size
    """
    cache = Cache(cache_size)

    tiles_data = []
    tile_file_names = []
    for root, subFolders, files in os.walk(tile_directory):
        for tile_name in files:
            if tile_name.endswith(".jpeg") or tile_name.endswith(".JPG"):
                tile_file_names.append(os.path.join(root, tile_name))
    user_img = Image.open(img_file_path)
    user_img = user_img.resize((user_img_len, user_img_breadth))
    user_img_data = np.array(user_img)
    column_list = []
    img_index_dict = {}
    for r in range(user_img_breadth):
        row_list = []
        for c in range(user_img_len):
            index = ((r % tile_to_user_img_pixel_ratio), (c % tile_to_user_img_pixel_ratio))
            img_index = (int(r / tile_to_user_img_pixel_ratio), int(c / tile_to_user_img_pixel_ratio))
            if img_index not in img_index_dict:
                img_index_dict[img_index] = random.randrange(len(tile_file_names))
            tile_split_img = get_tile_split_img_dict(cache, img_index_dict[img_index], tile_file_names, tile_size, tile_to_user_img_pixel_ratio)[index]
            tint_img = Image.new('RGB', tile_split_img.size, tuple(user_img_data[r, c]))
            new_data = np.array(Image.blend(tile_split_img, tint_img, 0.8))
            print(r, c, user_img_breadth, user_img_len, tile_size, user_img_data[r, c])
            row_list.append(new_data)
        column_list.append(np.concatenate(row_list, axis=1))
        del row_list
    new_img_data = np.concatenate(column_list, axis=0)
    del column_list
    new_img = Image.fromarray(new_img_data).convert('RGB')
    new_img.save(final_img_file_path)


if __name__ == '__main__':
    main()
