import threading
import logging
from util.logger_super import LoggerSuper
from util.base_class import BaseClass
from queue import Queue


class Keyboard(LoggerSuper):
    """
    Класс реализует поток чтение и обработку команд из консоли
    """
    logger = logging.getLogger('Keyboard')

    def __init__(self, observers=None):
        # Start keyboart queue thread
        self.observers = []
        if observers is not None:
            if isinstance(observers, list):
                for _observer in observers:
                    self.observers.append(_observer)
            else:
                self.observers.append(observers)
        self.queue = Queue(maxsize=3)

        self.inputThread = threading.Thread(target=self.read_kbd_input, args=(), daemon=False)
        self.inputThread.start()
        self.logger.info('start keyboard thread')

    def add_observer(self, observer):
        self.observers.append(observer)

    def del_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.keyboard_notify(self)

    def get(self):
        return self.queue.get()

    # Function of input in thread
    def read_kbd_input(self):
        while BaseClass.working():
            # Receive keyboard input from user.
            input_str = input()
            print('Enter command: ' + input_str)
            cmd_list = input_str.split(' ')
            if len(cmd_list) > 0:
                if 'exit' in cmd_list:
                    BaseClass.exit()
                else:
                    self.queue.put(cmd_list)
                    self.notify_observers()