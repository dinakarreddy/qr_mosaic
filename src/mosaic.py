from PIL import Image
import numpy as np
import os
import random


def get_tile_split_masks(split_len, data):
    data_dict = {}
    qr_len = len(data)
    n = int(qr_len/split_len)
    for i in range(split_len):
        for j in range(split_len):
            i_end_index = (i+1)*n
            j_end_index = (j+1)*n
            if i == split_len - 1:
                i_end_index = None
            if j == split_len - 1:
                j_end_index = None
            data_dict[(i, j)] = np.copy(data[i*n:i_end_index, j*n:j_end_index])
    return data_dict


def main():
    img_file_path = '/qr/images/1.jpeg'
    final_img_file_path = '/qr/images/result_images/mosaic.jpeg'
    tile_directory = '/qr/images/image_set'
    tile_to_user_img_pixel_ratio = 50
    tile_size = 500
    tiles_data = []
    for filename in os.listdir(tile_directory):
        if filename.endswith(".jpeg"):
            tiles_data.append(np.array(
                Image.open(os.path.join(tile_directory, filename)).convert('RGB').resize((tile_size, tile_size))))
    user_img = Image.open(img_file_path)
    user_img_len, user_img_breadth = 500, 500
    user_img = user_img.resize((user_img_len, user_img_breadth))
    user_img_data = np.array(user_img)
    tiles_split_data_dict = [get_tile_split_masks(tile_to_user_img_pixel_ratio, tile_data) for tile_data in tiles_data]
    tiles_split_img_dict = []
    for tile_split_data_dict in tiles_split_data_dict:
        tiles_split_img_dict.append({index: Image.fromarray(value) for index, value in tile_split_data_dict.items()})
    del tiles_split_data_dict, tiles_data
    column_list = []
    img_index_dict = {}
    for r in range(user_img_breadth):
        row_list = []
        for c in range(user_img_len):
            index = ((r % tile_to_user_img_pixel_ratio), (c % tile_to_user_img_pixel_ratio))
            img_index = (int(r/tile_to_user_img_pixel_ratio), int(c/tile_to_user_img_pixel_ratio))
            if img_index not in img_index_dict:
                img_index_dict[img_index] = random.randrange(len(tiles_split_img_dict))
            tile_split_img = tiles_split_img_dict[img_index_dict[img_index]][index]
            tint_img = Image.new('RGB', tile_split_img.size, tuple(user_img_data[r, c]))
            new_data = np.array(Image.blend(tile_split_img, tint_img, 0.2))
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
