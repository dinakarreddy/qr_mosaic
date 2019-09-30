import argparse
import os
import sys
from copy import deepcopy

import numpy as np
from PIL import Image

TARGET_IMAGE_RESIZE_FACTOR = 2
TILE_WIDTH = 50
TILE_HEIGHT = 50
TILES_DIRECTORY = 'images/image_set'
FINAL_IMAGE_TYPE = 'RGB'
SAVE_FOR_EACH_TILE = True


def tiles_file_path_yielder(tiles_directory):
    for root, subFolders, files in os.walk(tiles_directory):
        for tile_name in files:
            if tile_name.endswith(".jpeg"):
                yield os.path.join(root, tile_name)


class TargetImage:
    def __init__(self, target_img_file_path):
        self.target_img_file_path = target_img_file_path
        self.img = TargetImage._get_img(self.target_img_file_path)
        width, height = self.img.size
        self.img = self.img.resize(
            (width * TARGET_IMAGE_RESIZE_FACTOR, height * TARGET_IMAGE_RESIZE_FACTOR),
            Image.ANTIALIAS)
        self.width, self.height = self.img.size
        self.img_data = np.array(self.img)

    @staticmethod
    def _get_img(file_path):
        # url = "http://example_image.com"
        # img = Image.open(urlopen(url))
        img = Image.open(file_path).convert('RGB')
        return img


def get_replacement_tile(target_tile, tiles_paths):
    min_diff = float('inf')
    min_diff_tile = None
    target_tile = target_tile.astype('int32')
    for tile_path in tiles_paths:
        tile = np.array(Image.open(tile_path).resize(
            (TILE_WIDTH, TILE_HEIGHT), Image.ANTIALIAS).convert('RGB'))[
               :len(target_tile), :len(target_tile[0])]
        diff_tile = target_tile - tile.astype('int32')
        diff = np.sum(diff_tile ** 2)
        if diff < min_diff:
            min_diff_tile = tile
            min_diff = diff
    return min_diff_tile


def main(target_img_file_path, tiles_directory, final_img_file_path):
    target_image_obj = TargetImage(target_img_file_path)
    tiles_paths = [tile_path for tile_path in tiles_file_path_yielder(TILES_DIRECTORY)]
    if not tiles_paths:
        raise Exception("No tile images found")
    total_tile_images = len(tiles_paths)
    print('total tile images: {total_tile_images}'.format(total_tile_images=total_tile_images))
    final_img_data = deepcopy(target_image_obj.img_data)
    total_height = target_image_obj.height
    total_width = target_image_obj.width
    for w in range(0, total_height, TILE_HEIGHT):
        for h in range(0, total_width, TILE_WIDTH):
            sys.stdout.write("\r{}, {}, {}, {}".format(total_width, total_height, w, h))
            sys.stdout.flush()
            target_tile = final_img_data[w:w + TILE_WIDTH, h:h + TILE_HEIGHT]
            replacement_tile = get_replacement_tile(target_tile, tiles_paths)
            final_img_data[w:w + TILE_WIDTH, h:h + TILE_HEIGHT] = replacement_tile[
                                                                  :len(target_tile),
                                                                  :len(target_tile[0])]
            if SAVE_FOR_EACH_TILE:
                temp_img = Image.fromarray(final_img_data).convert(FINAL_IMAGE_TYPE)
                temp_img.save(final_img_file_path)
    final_img = Image.fromarray(final_img_data).convert(FINAL_IMAGE_TYPE)
    final_img.save(final_img_file_path)
    print("\nFinal image saved: {}".format(final_img_file_path))


def mosaic_best_fit_parser(arguments):
    parser = argparse.ArgumentParser(description='Generate qrs with user provided images')
    parser.add_argument('--target_img_file_path',
                        dest='target_img_file_path',
                        help='image which needs to be created through mosaic',
                        default="/qr/images/1.jpeg",
                        )
    parser.add_argument('--tiles_directory',
                        dest='tiles_directory',
                        help='all images that are used to create mosaic',
                        default="/qr/images/image_set",
                        )
    parser.add_argument('--final_img_file_path',
                        dest='final_img_file_path',
                        help='final_img_file_path, final image location to be saved',
                        default="/qr/images/result_images/mosaic_best_fit.jpeg",
                        )
    parser.add_argument('--tile_size',
                        dest='tile_size',
                        help='size of each tile in pixels',
                        default=50,
                        )
    parser.add_argument('--final_img_type',
                        dest='final_img_type',
                        help='final image type: RGB/B&W/pencil',
                        default='RGB',
                        )
    return parser.parse_args(arguments)


if __name__ == '__main__':
    parsed = mosaic_best_fit_parser(sys.argv[1:])
    main(parsed.target_img_file_path, parsed.tiles_directory, parsed.final_img_file_path)
