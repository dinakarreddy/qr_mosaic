import argparse
import pyqrcode
from PIL import Image
import io
import math
import numpy as np
import scipy.ndimage
import sys
# from urllib.request import urlopen


def grayscale(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


def dodge(front, back):
    result = front * 255 / (255 - back)
    result[result > 255] = 255
    result[back == 255] = 255
    return result.astype('uint8')


def get_qr_img(data, quiet_zone):
    qr = pyqrcode.create(data, error='H')
    buffer = io.BytesIO()
    qr.png(buffer, quiet_zone=quiet_zone)
    qr_img = Image.open(buffer)
    return qr_img


def get_user_img(file_path):
    # url = "https://qph.fs.quoracdn.net/main-qimg-1a01d5a16d7d450f642449534ac50680"
    # img = Image.open(urlopen(url))
    img = Image.open(file_path)
    return img


def get_qr_split_masks(split_len, qr_data):
    mask_dict = {}
    data_dict = {}
    qr_len = len(qr_data)
    n = int(qr_len/split_len)
    qr_mask = (qr_data == [0, 0, 0]).all(2)
    false_mask = np.copy(qr_mask)
    false_mask[:, :] = False
    for i in range(split_len):
        for j in range(split_len):
            i_end_index = (i+1)*n
            j_end_index = (j+1)*n
            if i == split_len - 1:
                i_end_index = None
            if j == split_len - 1:
                j_end_index = None
            mask_dict[(i, j)] = np.copy(qr_mask[i*n:i_end_index, j*n:j_end_index])
            data_dict[(i, j)] = np.copy(qr_data[i*n:i_end_index, j*n:j_end_index])
    return mask_dict, data_dict


def get_pencil_image(img):
    gray_data = grayscale(np.array(img))
    inverted_gray = 255 - gray_data
    blurred_inverted_gray = scipy.ndimage.filters.gaussian_filter(inverted_gray, sigma=60)
    pencil_data = dodge(blurred_inverted_gray, gray_data)
    return Image.fromarray(pencil_data)


def main(qr_data, img_file_path, final_img_file_path, final_img_type,
         qr_to_user_img_pixel_ratio, max_user_img_size, qr_quiet_zone):
    qr_img = get_qr_img(qr_data, qr_quiet_zone).convert('RGB')
    qr_len = min(qr_img.size)
    qr_len = max(qr_to_user_img_pixel_ratio, qr_len)
    qr_img = qr_img.resize((qr_len, qr_len))
    user_img = get_user_img(img_file_path)
    if final_img_type == 'pencil':
        user_img = get_pencil_image(user_img)
    user_img = user_img.convert('RGB')
    user_img_len, user_img_breadth = user_img.size
    if user_img_len >= user_img_breadth:
        ratio = float(user_img_breadth)/user_img_len
        max_user_img_len = max_user_img_size
        max_user_img_breadth = int(ratio*max_user_img_size)
    else:
        ratio = float(user_img_len) / user_img_breadth
        max_user_img_len = int(ratio * max_user_img_size)
        max_user_img_breadth = max_user_img_size
    user_img_len, user_img_breadth = min(user_img_len, max_user_img_len), min(user_img_breadth, max_user_img_breadth)
    user_img = user_img.resize((user_img_len, user_img_breadth))

    qr_data = np.array(qr_img)
    user_img_data = np.array(user_img)

    mask_dict, data_dict = get_qr_split_masks(qr_to_user_img_pixel_ratio, qr_data)
    column_list = []
    for r in range(user_img_breadth):
        row_list = []
        for c in range(user_img_len):
            index = ((r % qr_to_user_img_pixel_ratio), (c % qr_to_user_img_pixel_ratio))
            new_data = np.copy(data_dict[index])
            new_data[mask_dict[index]] = user_img_data[r, c]
            print(r, c, user_img_breadth, user_img_len, len(qr_data), user_img_data[r, c])
            row_list.append(new_data)
        column_list.append(np.concatenate(row_list, axis=1))
        del row_list
    new_img_data = np.concatenate(column_list, axis=0)
    del column_list
    new_img = Image.fromarray(new_img_data).convert('RGB')
    if final_img_type != 'RGB':
        new_img = new_img.convert('L')
    new_img.save(final_img_file_path)


def generate_qr_parser(arguments):
    parser = argparse.ArgumentParser(description='Generate qrs with user provided images')
    parser.add_argument('--qr_data',
                        dest='qr_data',
                        help='qr data to be encoded',
                        default='https://www.google.co.in/maps/place/Pedda+Yammanur,+Andhra+Pradesh+518155/@15.0674719,78.3384526,12z/data=!4m5!3m4!1s0x3bb468535b6d25a3:0x37d208b2f7f8ce0!8m2!3d15.0686611!4d78.4304294',
                        )
    parser.add_argument('--img_file_path',
                        dest='img_file_path',
                        help='img_file_path, image to be generated with qr',
                        default="/qr/user_img.jpeg",
                        )
    parser.add_argument('--final_img_file_path',
                        dest='final_img_file_path',
                        help='final_img_file_path, final image location to be saved',
                        default="/qr/new_user_img.jpeg",
                        )
    parser.add_argument('--final_img_type',
                        dest='final_img_type',
                        help='final image type: RGB/B&W/pencil',
                        default='RGB',
                        )
    parser.add_argument('--qr_to_user_img_pixel_ratio',
                        dest='qr_to_user_img_pixel_ratio',
                        help='Number of pixels in user img should each qr image cover',
                        type=int,
                        default=10,
                        )
    parser.add_argument('--max_user_img_size',
                        dest='max_user_img_size',
                        help='Max Number of pixels in user img. Input user Image will be resized if greater than this',
                        type=int,
                        default=1000,
                        )
    parser.add_argument('--qr_quiet_zone',
                        dest='qr_quiet_zone',
                        help='qr_quiet_zone, white space around each qr which is needed for detecting qr',
                        type=int,
                        default=1,
                        )
    return parser.parse_args(arguments)


if __name__ == '__main__':
    parsed = generate_qr_parser(sys.argv[1:])
    main(
        parsed.qr_data,
        parsed.img_file_path,
        parsed.final_img_file_path,
        parsed.final_img_type,
        parsed.qr_to_user_img_pixel_ratio,
        parsed.max_user_img_size,
        parsed.qr_quiet_zone,
    )
