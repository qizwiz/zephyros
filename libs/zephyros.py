import socket
import threading
import json
import Queue
import sys
import atexit
import itertools


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 1235))

raw_message_queue = Queue.Queue(10)
reified_msg_id_gen = itertools.count()
send_data_queue = Queue.Queue(10)
individual_message_queues = {}


def run_in_background(fn):
    t = threading.Thread(target=fn)
    t.daemon = True
    t.start()

@run_in_background
def read_forever():
    while True:
        len_str = ''
        while True:
            in_str = sock.recv(1)
            if in_str == '\n':
                 break
            len_str += in_str

        len_num = int(len_str)
        data = ''
        while len(data) < len_num:
            new_data = sock.recv(len_num)
            len_num -= len(new_data)
            data += new_data

        obj = json.loads(data)
        raw_message_queue.put(obj)

@run_in_background
def send_data_fully():
    while True:
        data = send_data_queue.get()
        while len(data) > 0:
            num_wrote = sock.send(data)
            data = data[num_wrote:]


def send_message(msg, infinite=True, callback=None):
    msgId = reified_msg_id_gen.next()
    temp_send_queue = Queue.Queue(10)
    individual_message_queues[msgId] = temp_send_queue

    msg.insert(0, msgId)
    msg_str = json.dumps(msg)
    send_data_queue.put(str(len(msg_str)) + '\n' + msg_str)

    if callback is not None:
        def temp_fn():
            temp_send_queue.get() # ignore first
            if infinite:
                while True:
                    obj = temp_send_queue.get()
                    callback(obj[1])
            else:
                obj = temp_send_queue.get()
                callback(obj[1])
        run_in_background(temp_fn)
        return None
    else:
        return temp_send_queue.get()[1]


@run_in_background
def dispatch_individual_messages_forever():
    while True:
        msg = raw_message_queue.get()
        msg_id = msg[0]
        this_queue = individual_message_queues[msg_id]
        this_queue.put(msg)

def zephyros(fn):
    run_in_background(fn)
    try:
        while True: pass
    except KeyboardInterrupt:
        pass


class Rect:
    @classmethod
    def from_dict(cls, d):
        return cls(x=d['x'],
                   y=d['y'],
                   w=d['w'],
                   h=d['h'])
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = w
        self.y = y
        self.w = w
        self.h = h

class Point:
    @classmethod
    def from_dict(cls, d):
        return cls(x=d['x'],
                   y=d['y'])
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Size:
    @classmethod
    def from_dict(cls, d):
        return cls(w=d['w'],
                   h=d['h'])
    def __init__(self, w=0, h=0):
        self.w = w
        self.h = h

class Proxy:
    def __init__(self, id): self.id = id
    def _send_sync(self, *args): return send_message([self.id] + list(args))

class Window(Proxy):
    def title(self): return self._send_sync('title')
    def frame(self): return Rect.from_dict(self._send_sync('frame'))
    def top_left(self): return Point.from_dict(self._send_sync('top_left'))
    def size(self): return Size.from_dict(self._send_sync('size'))
    def set_frame(self, f): self._send_sync('set_frame', vars(f))
    def set_top_left(self, tl): return self._send_sync('set_top_left', vars(tl))
    def set_size(self, s): return self._send_sync('set_size', vars(s))
    def maximize(self): return self._send_sync('maximize')
    def minimize(self): return self._send_sync('minimize')
    def un_minimize(self): return self._send_sync('un_minimize')
    def app(self): return App(self._send_sync('app'))
    def screen(self): return Screen(self._send_sync('screen'))
    def focus_window(self): return self._send_sync('focus_window')
    def focus_window_left(self): return self._send_sync('focus_window_left')
    def focus_window_right(self): return self._send_sync('focus_window_right')
    def focus_window_up(self): return self._send_sync('focus_window_up')
    def focus_window_down(self): return self._send_sync('focus_window_down')
    def normal_window(self): return self._send_sync('normal_window')
    def minimized(self): return self._send_sync('minimized')
    def other_windows_on_same_screen(self): return map(Window, self._send_sync('other_windows_on_same_screen'))
    def other_windows_on_all_screens(self): return map(Window, self._send_sync('other_windows_on_all_screens'))

class Screen(Proxy):
    def frame_including_dock_and_menu(self): return Rect.from_dict(self._send_sync("frame_including_dock_and_menu"))
    def frame_without_dock_or_menu(self): return Rect.from_dict(self._send_sync("frame_without_dock_or_menu"))
    def previous_screen(self): return Screen(self._send_sync("previous_screen"))
    def next_screen(self): return Screen(self._send_sync("next_screen"))

class App(Proxy):
    def visible_windows(self): return map(Window, self._send_sync("visible_windows"))
    def all_windows(self): return map(Window, self._send_sync("all_windows"))
    def title(self): return self._send_sync("title")
    def hidden(self): return self._send_sync("hidden")
    def show(self): return self._send_sync("show")
    def hide(self): return self._send_sync("hide")
    def kill(self): return self._send_sync("kill")
    def kill9(self): return self._send_sync("kill9")

class Api(Proxy):
    def alert(self, msg, duration=1): self._send_sync('alert', msg, duration)
    def log(self, msg): self._send_sync('log', msg)
    def relaunch_config(self): self._send_sync('relaunch_config')
    def clipboard_contents(self): return self._send_sync('clipboard_contents')
    def focused_window(self): return Window(self._send_sync('focused_window'))
    def visible_windows(self): return map(Window, self._send_sync('visible_windows'))
    def all_windows(self): return map(Window, self._send_sync('all_windows'))
    def main_screen(self): return Screen(self._send_sync('main_screen'))
    def all_screens(self): return map(Screen, self._send_sync('all_screens'))
    def running_apps(self): return map(App, self._send_sync('running_apps'))
    def bind(self, key, mods, fn):
        def tmp_fn(obj): fn()
        send_message([0, 'bind', key, mods], callback=tmp_fn)
    def choose_from(self, lst, title, lines, chars, fn):
        send_message([0, 'choose_from', lst, title, lines, chars], callback=fn, infinite=False)
    def listen(self, event, fn):
        def tmp_fn(obj):
            if event == "window_created":       fn(Window(obj))
            elif event == "window_minimized":   fn(Window(obj))
            elif event == "window_unminimized": fn(Window(obj))
            elif event == "window_moved":       fn(Window(obj))
            elif event == "window_resized":     fn(Window(obj))
            elif event == "app_launched":       fn(App(obj))
            elif event == "app_died":           fn(App(obj))
            elif event == "app_hidden":         fn(App(obj))
            elif event == "app_shown":          fn(App(obj))
            elif event == "screens_changed":    fn()
        send_message([0, 'listen', event], callback=tmp_fn)

api = Api(0)
