import threading
import time
import json
import schedule
from DataAccess import DBA, DAO
from Config import Config
from DeviceCom import MessageHandler, DisplayController
from Plots import DisplayPlot


class PeriodicDisplayTask(threading.Thread):
    def __init__(self):
        """
        Display event scheduler - periodically read tasks from task file (JSON) and schedule events
        Read data from DB >> render plot >> convert plot to standard format (display size ong or byte array) >> 
            >> obtain MQTT connection from MessageHandler >> pass data to Display controller >> 
            >> [DisplayController] convert image to line format >> [DisplayController] transmit via MQTT
        """
        threading.Thread.__init__(self)
        self.conf = Config.Config().get_config()
        self.schedule_file_name = self.conf.get('scheduler', 'task_file')
        self.interval = self.conf.getint('scheduler', 'schedule_interval')
        self.screen_index = {}  # help with screen rotation
        self.last_time_index = {}  # help with event scheduling
        self.last_time = time.time()
        self.db = DBA.Dba(self.conf.get('db', 'path'))

    def _do_task(self, task_json):
        """
        Get display from DB, prepare data and send to device via MQTT
        :param task_json: 
        :return: 
        """
        print("starting task")
        device_id = task_json.get('device_id')
        display_name = task_json.get('display_name')

        screens = self.db.get_display(device_id, display_name)  # all screen from single display
        screen = None  # current screen
        key = str(device_id) + ':' + str(display_name)

        # rotates between all display screen
        if str.format(key) in self.screen_index:
            current_index = self.screen_index[key] + 1 if (self.screen_index[key] + 1) < len(screens) else 0
            self.screen_index[key] = current_index

            screen = screens[current_index]
        else:  # new screen task
            self.screen_index[key] = 0
            screen = screens[0]

        # handle MQTT connection
        mqtt_handler = MessageHandler.MessageHandler(self.conf.get('mqtt', 'ip'), self.conf.getint('mqtt', 'port'))
        # provide display remote control functions
        display_controller = DisplayController.DisplayController(mqtt_handler.get_client_instance(),
                                                                 str.format("{}/{}/{}",
                                                                            self.conf.get('discovery', 'base_msg'),
                                                                            device_id, display_name))

        # TODO move this logic to DB layer
        screen_action = json.loads(screen.params)
        records = self.db.get_record_from_device(screen_action.get('source_device'),
                                                 screen_action.get('source_ability'),
                                                 limit=self.conf.getint('db', 'default_records_limit'))
        # TODO implement time interval from date - to date
        values = [float(record.value) for record in records]
        values.reverse()

        plot = DisplayPlot.DisplayPlot(values, x_label_rotation=90)
        plot.render_to_png(key + '.png', width=320, height=240)

        # TODO convert plot to bitmap with display size
        # TODO send to MQTT
        # display_controller.draw_bitmap()
        print(screen)

    def _create_tasks(self):
        tasks_json = None
        with open(self.schedule_file_name, 'r') as file:  # load task JSON
            try:
                tasks_json = json.loads(file.read())
            except IOError:
                print("Error cant read scheduler file")
            except json.JSONDecodeError:
                print("Error cant convert JSON file")

        time_now = time.time()
        for task in tasks_json:  # create new scheduled task
            print(task)
            schedule.every(task.get('interval', 1)).seconds.do(self._do_task, task)

    def run(self):
        """
        Every schedule_interval starts all pending tasks
        :return: 
        """
        print("scheduled start")
        self._create_tasks()
        # TODO detect changes in file and update tasks
        # schedule doc https://schedule.readthedocs.io/en/stable/faq.html#how-can-i-run-a-job-only-once

        while True:
            print('.')
            schedule.run_pending()
            time.sleep(self.interval)
