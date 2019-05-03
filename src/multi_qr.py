import pyqrcode
from PIL import Image
import io
import math
import numpy as np
import scipy.ndimage
from urllib.request import urlopen


def grayscale(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


def dodge(front, back):
    result = front * 255 / (255 - back)
    result[result > 255] = 255
    result[back == 255] = 255
    return result.astype('uint8')


def get_qr_img():
    # data = "0123456789abcdefghijklmnopqrstuvwxyz"
    data = "https://drive.google.com/drive/u/0/folders/0B4S8L74EnzaZfnQ1VExKUFMwYnFFcENQeGNOV1hQUm1idXV1QmtZYVJxelhFcnY1Y2hzTms"
    qr = pyqrcode.create(data, error='H')
    buffer = io.BytesIO()
    # qr.png(buffer)
    qr.png(buffer, quiet_zone=1)
    qr_img = Image.open(buffer).convert('RGB')
    return qr_img


def get_user_img():
    url = "https://qph.fs.quoracdn.net/main-qimg-1a01d5a16d7d450f642449534ac50680"
    # img = Image.open(urlopen(url))
    img = Image.open("/qr/user_img.jpeg").convert('RGB')
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


def main():
    qr_to_user_img_pixel_ratio = 100
    qr_img = get_qr_img().convert('RGB')
    qr_len = min(qr_img.size)
    qr_len = max(qr_to_user_img_pixel_ratio, qr_len)
    qr_img = qr_img.resize((qr_len, qr_len))
    user_img = get_user_img().convert('RGB')
    user_img_len, user_img_breadth = user_img.size
    max_size = 1000
    # max_user_img_len, max_user_img_breadth = 100, 100
    if user_img_len >= user_img_breadth:
        ratio = float(user_img_breadth)/user_img_len
        max_user_img_len = max_size
        max_user_img_breadth = int(ratio*max_size)
    else:
        ratio = float(user_img_len) / user_img_breadth
        max_user_img_len = int(ratio * max_size)
        max_user_img_breadth = max_size
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
    new_img = Image.fromarray(new_img_data)
    new_img.save("new_img.png")


if __name__ == '__main__':
    main()
