import time

import pyautogui
import pynput

trace = []
press_flag = False
start_time = end_time = time.time()
total_time = 0
total_length = 0


def _on_move(x, y):
    global trace, press_flag, start_time, end_time, total_time
    end_time = time.time()
    if press_flag:
        # print('鼠标位置: {}'.format((x, y)))
        diff_time = end_time - start_time
        if diff_time > 0.02 and press_flag:
            point = {'x': x, 'y': y, 'time': diff_time}
            trace.append(point)
            print('鼠标当前位置: {}'.format(point))
            total_time += diff_time
            start_time = time.time()


def _on_click(x, y, button, pressed):
    global trace, press_flag, start_time, end_time, total_time, total_length
    # 监听鼠标点击
    if pressed:
        print("鼠标点击")
        mxy = "{},{}".format(x, y)
        print(mxy)
        print(button)
        press_flag = True
        trace.append({'x': x, 'y': y, 'time': 0.0})
        start_time = time.time()
        # return False
    if not pressed:
        print("鼠标释放")
        mxy = "{},{}".format(x, y)
        # Stop listener
        press_flag = False
        end_time = time.time()
        trace.append({'x': x, 'y': y, 'time': end_time - start_time})
        total_time += end_time - start_time
        total_length = trace[-1]['x'] - trace[0]['x']
        print('total_length: {}  total_time: {}'.format(total_length, total_time))
        return False


def get_trace():
    global trace, total_length, total_time
    trace = []
    total_time = total_length = 0
    with pynput.mouse.Listener(on_click=_on_click, on_move=_on_move) as listener:
        listener.join()
    return trace, total_length, total_time


if __name__ == '__main__':
    # while True:
    #     curr = time.time()
    #     trace = []
    #     position = pyautogui.position()
    #     point = {'x': position.x, 'y': position.y, 'time': time.time() - curr}
    #     trace.append(point)
    #     # print("x: {} y: {}".format(position.x, position.y))
    #     print(point)
    #     time.sleep(0.2)
    # with pynput.mouse.Listener(on_click=_on_click, on_move=_on_move) as listener:
    #     listener.join()

    print(get_trace())
