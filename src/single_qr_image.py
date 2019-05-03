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
    qr = pyqrcode.create(data, error='H', version=40)
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


def get_resized_square_images(qr_img, user_img):
    qr_img_size = min(qr_img.size)
    _min = min(user_img.size)
    assert _min > qr_img_size
    scale = int(_min / qr_img_size)
    scaled_count = scale * qr_img_size
    qr_img = qr_img.resize((scaled_count, scaled_count))
    # ratio_of_img_to_qr = 0.4
    ratio_of_img_to_qr = 1
    user_img_scale_count = int(scaled_count * ratio_of_img_to_qr)
    user_img = user_img.resize((user_img_scale_count, user_img_scale_count))
    return qr_img, user_img


def get_overlapped_image(qr_img, user_img):
    qr_img_length = qr_img.size[0]
    user_img_length = user_img.size[0]
    diff = math.ceil((qr_img_length - user_img_length) / 2)
    overlapped_data = np.zeros((qr_img_length, qr_img_length, 3), dtype=np.uint8)
    for r in range(qr_img_length):
        for c in range(qr_img_length):
            if qr_img_length - diff < r or r < diff or qr_img_length - diff < c or c < diff:
                # overlapped_data[r, c] = qr_img.getpixel((r, c))
                overlapped_data[r, c] = [255, 255, 255]
            else:
                overlapped_data[r, c] = user_img.getpixel((c - diff, r - diff))
    overlapped_image = Image.fromarray(overlapped_data).convert('RGB')
    return overlapped_image


def main():
    qr_img = get_qr_img()
    user_img = get_user_img()
    qr_img, user_img = get_resized_square_images(qr_img, user_img)
    overlapped_image = get_overlapped_image(qr_img, user_img)
    overlapped_image = Image.blend(overlapped_image, qr_img, 0.3)
    overlapped_image.save('overlapped_image.png')
    qr_img.save('qr_image.png')
    print("Done!!")


if __name__ == '__main__':
    main()
