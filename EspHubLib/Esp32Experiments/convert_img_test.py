from PIL import Image
import sys


def print_bmp(bytes, columns=8):
    for row in range(0, int(len(bytes) / columns)):
        for column in range(0, columns):
            if row * columns + column >= len(bytes):
                return
            print('{}'.format(bytes[row * columns + column]), end=' ')
        print()


def bitmap_to_xbm(xmb_bytes, height, width):
    output = "#define img_width {}\n#define img_height {}\nstatic char img_bits[]".format(width, height)
    output += " = {\n"
    for byte in xmb_bytes:
        output += '0x{:02X}, '.format(byte)
    output += '};'
    return output


def convert_bitmap_to_xbm_raw(bitmap_bytes):
    xbm_lst = []
    try:
        for i in range(0, len(bitmap_bytes), 8):
            # print(i, end=' ')
            pixel_byte = 0
            for bit in range(7, -1, -1):
                pixel_byte <<= 1
                pixel_byte |= bitmap_bytes[i + bit]
                # print(i+bit, end=' ')
            # print('0x{:02X},'.format(pixel_byte), end=' ')
            xbm_lst.append(pixel_byte)
    except IndexError: 
        print('end')

    return xbm_lst


if __name__ == "__main__":
    img = Image.open(sys.argv[1])
    img_bytes = img.tobytes()
    # print_bmp(img_bytes)
    print('Len of img bytes:', len(img_bytes))

    xbm = convert_bitmap_to_xbm_raw(img_bytes)
    print()
    print('Len of xbm bytes:', len(xbm))

    with open('tttast.xbm', 'w') as f:
        f.write(bitmap_to_xbm(xbm, 64, 64))
    # for i in xbm:
    # print('{:02X}'.format(i), end=' ')

