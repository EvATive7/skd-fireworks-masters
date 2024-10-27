import cv2
import numpy as np
import os
import time
from subprocess import Popen, PIPE
import os
import logging
import config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


new_path = "./bin/adb"
os.environ["PATH"] += os.pathsep + new_path


def delete_all_files_in_directory(directory):
    """
    删除指定目录下的所有文件。

    参数:
    directory (str): 要删除文件的目录路径
    """
    # 遍历指定目录
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # 检查是否为文件（而不是子目录）
        if os.path.isfile(file_path):
            os.remove(file_path)  # 删除文件
            logging.debug(f"已删除文件: {file_path}")


delete_all_files_in_directory('cache')


# 连接设备函数
def connect_device():
    os.system(f"adb connect {config.DEVICE_ADDRESS}")

# 截图并传输到本地


def capture_screenshot():
    import time
    timet = time.time()
    logging.debug(f'截图{timet}.png')
    os.system("adb shell screencap -p /sdcard/screen.png")
    os.system(f"adb pull /sdcard/screen.png ./cache/{timet}.png")
    return cv2.imread(f"./cache/{timet}.png")

# 模板匹配，返回是否匹配成功及点击坐标


def match_template(screenshot, template_path):
    logging.debug(f"正在匹配 {template_path}")

    # 读取彩色模板图像
    template = cv2.imread(template_path)
    if template is None:
        logging.debug("无法读取模板图像")
        return False, 0, 0

    # 确保截屏是彩色图像
    if screenshot.ndim != 3 or screenshot.shape[2] != 3:
        logging.debug("截屏图像不是彩色图像")
        return False, 0, 0

    # 进行模板匹配
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    threshold = 0.9  # 设置匹配阈值
    if max_val > threshold:
        click_x, click_y = max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2
        logging.debug(f"匹配成功 ({click_x}, {click_y})")
        return True, click_x, click_y
    else:
        logging.debug("未找到匹配内容")
        return False, 0, 0


def recognize_matrix(screenshot, top_left, bottom_right, target_color="purple"):
    """
    识别5x5矩阵，将指定颜色标记为1，其他颜色标记为0。

    参数：
    - screenshot: 截图图像
    - top_left: 左上角坐标 (x, y)
    - bottom_right: 右下角坐标 (x, y)
    - target_color: 字符串，"purple" 或 "red"，选择标记1的目标颜色

    返回：
    - 5x5矩阵，其中目标颜色为1，其他颜色为0
    """
    # 根据输入的坐标确定矩阵区域
    x1, y1 = top_left
    x2, y2 = bottom_right
    matrix_area = screenshot[y1:y2, x1:x2]

    # 颜色阈值
    color_thresholds = {
        "purple": ([108-20, 79-20, 205-20], [108+20, 79+20, 205+20]),
        "red": ([199-20, 43-20, 105-20], [199+20, 43+20, 105+20])
    }

    # 转换颜色空间为rgb
    colors = cv2.cvtColor(matrix_area, cv2.COLOR_BGR2RGB)
    matrix = np.zeros((5, 5), dtype=int)

    # 计算每个格子的宽度和高度
    cell_width = (x2 - x1) // 5
    cell_height = (y2 - y1) // 5

    # 获取目标颜色的rgb阈值
    lower_bound, upper_bound = color_thresholds[target_color]

    # 遍历5x5矩阵的每个格子
    for i in range(5):
        for j in range(5):
            # 计算每个格子的中心点
            center_x = (j * cell_width) + cell_width // 2
            center_y = (i * cell_height) + cell_height // 2

            # 获取中心点的rgb值
            RGB_value = colors[center_y, center_x]

            # 判断中心点的颜色是否在目标范围内
            if (lower_bound[0] <= RGB_value[0] <= upper_bound[0]) and \
               (lower_bound[1] <= RGB_value[1] <= upper_bound[1]) and \
               (lower_bound[2] <= RGB_value[2] <= upper_bound[2]):
                matrix[i, j] = 1  # 标记为1
            else:
                matrix[i, j] = 0  # 标记为0

    return matrix


def add_matrices_and_count_ones(matrix_a, matrix_b):
    """
    叠加两个充满0和1的矩阵，并计算结果中1的数量。

    参数:
    matrix_a (numpy.ndarray): 第一个矩阵
    matrix_b (numpy.ndarray): 第二个矩阵

    返回:
    tuple: (结果矩阵, 1的数量)
    """
    # 确保两个矩阵的形状相同
    if matrix_a.shape != matrix_b.shape:
        raise ValueError("两个矩阵的形状必须相同")

    # 矩阵叠加
    result_matrix = matrix_a + matrix_b

    # 计算结果矩阵中1的数量
    count_of_ones = np.sum(result_matrix > 0)

    return result_matrix, count_of_ones


def input_num(num: int):
    numstr = str(num)
    for char in numstr:
        addressx, addressy = config.NUMS_ADDRESS[char]
        os.system(f"adb shell input tap {addressx} {addressy}")
        time.sleep(0.7)


def wait_for_start():
    while True:
        screenshot = capture_screenshot()
        ismatched, x, y = match_template(screenshot, 'template/start.png')
        if ismatched:
            os.system(f"adb shell input tap {x} {y}")
            logging.debug("开始")
            break
        else:
            screenshot = capture_screenshot()
            ismatched, x, y = match_template(screenshot, 'template/cleargray.png')
            if ismatched:
                return
            time.sleep(3)
    pass


def count():
    total = 1
    while True:
        screenshot = capture_screenshot()

        ismatched_lapp, x, y = match_template(screenshot, 'template/lapp.png')
        ismatched_red, x, y = match_template(screenshot, 'template/clearred.png')
        if ismatched_lapp and not ismatched_red:
            logging.debug(f'==={total}===')
            time.sleep(1)
            screenshot = capture_screenshot()

            red_matrix = recognize_matrix(screenshot, **config.RED_CONFIG, target_color='red')
            logging.debug("红色矩阵：")
            logging.debug(red_matrix)

            purple_matrix = recognize_matrix(screenshot, **config.PERPLE_CONFIG, target_color='purple')
            logging.debug("紫色矩阵：")
            logging.debug(purple_matrix)

            result_matrix, count = add_matrices_and_count_ones(red_matrix, purple_matrix)
            logging.debug(f"叠加结果：\n, {result_matrix}, {count}")

            input_num(count)
            total += 1
            time.sleep(5)
        else:
            time.sleep(3)


def main():
    connect_device()

    wait_for_start()

    time.sleep(2)

    count()


if __name__ == "__main__":
    main()
