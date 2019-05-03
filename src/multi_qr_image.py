import pyqrcode
from PIL import Image
import io
import math
import numpy as np
import scipy.ndimage
from urllib.request import urlopen

GRAY_SCALED_QR_DICT = {}


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
    qr.png(buffer)
    # qr.png(buffer, quiet_zone=4)
    qr_img = Image.open(buffer).convert('RGB')
    return qr_img


def get_user_img():
    url = "https://qph.fs.quoracdn.net/main-qimg-1a01d5a16d7d450f642449534ac50680"
    # img = Image.open(urlopen(url))
    img = Image.open("/qr/user_img.jpeg")
    gray_data = grayscale(np.array(img))
    inverted_gray = 255 - gray_data
    blurred_inverted_gray = scipy.ndimage.filters.gaussian_filter(inverted_gray, sigma=60)
    pencil_data = dodge(blurred_inverted_gray, gray_data)
    img = Image.fromarray(pencil_data).convert('RGB')
    return img


def main():
    qr_img = get_qr_img().convert('L')
    user_img = get_user_img().convert('L')
    user_img_len, user_img_breadth = user_img.size
    max_user_img_len = 500
    max_user_img_breadth = 500
    user_img_len, user_img_breadth = min(user_img_len, max_user_img_len), min(user_img_breadth, max_user_img_breadth)
    user_img = user_img.resize((user_img_len, user_img_breadth))
    qr_data = np.array(qr_img)
    qr_mask = (qr_data == 0)
    user_img_data = np.array(user_img)
    column_list = []
    for r in range(user_img_len):
        row_list = []
        for c in range(user_img_breadth):
            new_data = np.copy(qr_data)
            new_data[qr_mask] = user_img_data[c, r]
            print(r, c, user_img_len, user_img_breadth, len(qr_data), user_img_data[c, r])
            row_list.append(new_data)
        column_list.append(np.concatenate(row_list, axis=0))
        del row_list
    overlapped_data = np.concatenate(column_list, axis=1)
    del column_list
    overlapped_image = Image.fromarray(overlapped_data).convert('L')
    overlapped_image.save("multi_qr_overlapped.png")


if __name__ == '__main__':
    main()
