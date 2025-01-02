import time
from contextlib import contextmanager

from .logger import logger
from .connection import MNTConnection, MNTServer, safe_connection
from . import config


class CommandBuilder(object):
    """Build command str for minitouch.

    You can use this, to custom actions as you wish::

        with safe_connection(_DEVICE_ID) as connection:
            builder = CommandBuilder()
            builder.down(0, 400, 400, 50)
            builder.commit()
            builder.move(0, 500, 500, 50)
            builder.commit()
            builder.move(0, 800, 400, 50)
            builder.commit()
            builder.up(0)
            builder.commit()
            builder.publish(connection)

    use `d.connection` to get `connection` from device
    """

    # TODO (x, y) can not beyond the screen size
    def __init__(self):
        self._content = ""
        self._delay = 0

    def append(self, new_content):
        self._content += new_content + "\n"

    def commit(self):
        """ add minitouch command: 'c\n' """
        self.append("c")

    def wait(self, ms):
        """ add minitouch command: 'w <ms>\n' """
        self.append("w {}".format(ms))
        self._delay += ms

    def up(self, contact_id):
        """ add minitouch command: 'u <contact_id>\n' """
        self.append("u {}".format(contact_id))

    def down(self, contact_id, x, y, pressure):
        """ add minitouch command: 'd <contact_id> <x> <y> <pressure>\n' """
        self.append("d {} {} {} {}".format(contact_id, x, y, pressure))

    def move(self, contact_id, x, y, pressure):
        """ add minitouch command: 'm <contact_id> <x> <y> <pressure>\n' """
        self.append("m {} {} {} {}".format(contact_id, x, y, pressure))

    def publish(self, connection, wait=False):
        """ apply current commands (_content), to your device """
        self.commit()
        final_content = self._content
        logger.info("send operation: {}".format(final_content.replace("\n", "\\n")))
        connection.send(final_content)

        if wait:
            time.sleep(self._delay / 1000 + config.DEFAULT_DELAY)
        else:
            time.sleep(self._delay / 1000)
        self.reset()

    def reset(self):
        """ clear current commands (_content) """
        self._content = ""
        self._delay = 0


class MNTDevice(object):
    """ minitouch device object

    Sample::

        device = MNTDevice(_DEVICE_ID)

        # It's also very important to note that the maximum X and Y coordinates may, but usually do not, match the display size.
        # so you need to calculate position by yourself, and you can get maximum X and Y by this way:
        print('max x: ', device.connection.max_x)
        print('max y: ', device.connection.max_y)

        # single-tap
        device.tap([(400, 600)])
        # multi-tap
        device.tap([(400, 400), (600, 600)])
        # set the pressure, default == 100
        device.tap([(400, 600)], pressure=50)

        # long-time-tap
        # for long-click, you should control time delay by yourself
        # because minitouch return nothing when actions done
        # we will never know the time when it finished
        device.tap([(400, 600)], duration=1000)
        time.sleep(1)

        # swipe
        device.swipe([(100, 100), (500, 500)])
        # of course, with duration and pressure
        device.swipe([(100, 100), (400, 400), (200, 400)], duration=500, pressure=50)

        # extra functions ( their names start with 'ext_' )
        device.ext_smooth_swipe([(100, 100), (400, 400), (200, 400)], duration=500, pressure=50, part=20)

        # stop minitouch
        # when it was stopped, minitouch can do nothing for device, including release.
        device.stop()
    """

    def __init__(self, device_id):
        self.device_id = device_id
        self.server = None
        self.connection = None
        self.start()

    def reset(self):
        self.stop()
        self.start()

    def start(self):
        # prepare for connection
        self.server = MNTServer(self.device_id)
        # real connection
        self.connection = MNTConnection(self.server.port)

    def stop(self):
        self.connection.disconnect()
        self.server.stop()

    def tap(self, points, pressure=100, duration=None, no_up=None):
        """
        tap on screen, with pressure/duration

        :param points: list, looks like [(x1, y1), (x2, y2)]
        :param pressure: default == 100
        :param duration:
        :param no_up: if true, do not append 'up' at the end
        :return:
        """
        points = [list(map(int, each_point)) for each_point in points]

        _builder = CommandBuilder()
        for point_id, each_point in enumerate(points):
            x, y = each_point
            _builder.down(point_id, x, y, pressure)
        _builder.commit()

        # apply duration
        if duration:
            _builder.wait(duration)
            _builder.commit()

        # need release?
        if not no_up:
            for each_id in range(len(points)):
                _builder.up(each_id)

        _builder.publish(self.connection)

    def swipe(self, points, pressure=100, duration=None, no_down=None, no_up=None, pid=0):
        """
        swipe between points, one by one

        :param points: [(400, 500), (500, 500)]
        :param pressure: default == 100
        :param duration:
        :param no_down: will not 'down' at the beginning
        :param no_up: will not 'up' at the end
        :return:
        """
        points = [list(map(int, each_point)) for each_point in points]

        _builder = CommandBuilder()
        point_id = pid

        # tap the first point
        if not no_down:
            x, y = points.pop(0)
            _builder.down(point_id, x, y, pressure)
            _builder.publish(self.connection, wait=True)

        # start swiping
        for each_point in points:
            x, y = each_point
            _builder.move(point_id, x, y, pressure)

            # add delay between points
            if duration:
                _builder.wait(duration)
            _builder.commit()

        _builder.publish(self.connection)

        # release
        if not no_up:
            _builder.up(point_id)
            _builder.publish(self.connection)

    # extra functions' name starts with 'ext_'
    def ext_smooth_swipe(
        self, points, pressure=100, duration=None, part=None, no_down=None, no_up=None, pid=0
    ):
        """
        smoothly swipe between points, one by one
        it will split distance between points into pieces

        before::

            points == [(100, 100), (500, 500)]
            part == 8

        after::

            points == [(100, 100), (150, 150), (200, 200), ... , (500, 500)]

        :param points:
        :param pressure:
        :param duration:
        :param part: default to 10
        :param no_down: will not 'down' at the beginning
        :param no_up: will not 'up' at the end
        :return:
        """
        if not part:
            part = 10

        points = [list(map(int, each_point)) for each_point in points]

        for each_index in range(len(points) - 1):
            cur_point = points[each_index]
            next_point = points[each_index + 1]

            offset = (
                int((next_point[0] - cur_point[0]) / part),
                int((next_point[1] - cur_point[1]) / part),
            )
            new_points = [
                (cur_point[0] + i * offset[0], cur_point[1] + i * offset[1])
                for i in range(part + 1)
            ]
            self.swipe(
                new_points,
                pressure=pressure,
                duration=duration,
                no_down=no_down,
                no_up=no_up,
                pid=pid
            )


class BlitzDevice(object):
    def __init__(self, device_id):
        self.device_id = device_id
        self.server = None
        self.connection = None
        self.max_x = None
        self.max_y = None
        self.start()

    def reset(self):
        self.stop()
        self.start()

    def start(self):
        # prepare for connection
        self.server = MNTServer(self.device_id)
        # real connection
        self.connection = MNTConnection(self.server.port)
        self.max_x = self.connection.max_x
        self.max_y = self.connection.max_y

    def stop(self):
        self.connection.disconnect()
        self.server.stop()

    def _check_list(self, input_variable):
        if not isinstance(input_variable, list):
            return [input_variable]
        else:
            return input_variable

    def swift_tap(self, points, fingers, pressure=100, duration=None):
        """
        tap on screen, with pressure/duration
        :param points: [(x1, y1)] 或 (x1, y1)
        :param fingers: 对应的手指编号 List or int
        :param pressure: 暂时无用，默认100
        :param duration: 阻塞停留时间
        """
        if len(points) == 0:
            return
        points = self._check_list(points)
        fingers = self._check_list(fingers)
        points = [list(map(int, point)) for point in points] # point的坐标必须是int

        _builder = CommandBuilder()
        # 按下down
        for ((x, y), fid) in zip(points, fingers):
            _builder.down(fid, x, y, pressure)
        _builder.commit()

        # 死睡眠模拟手指停留时间
        if duration:
            _builder.wait(duration)
            _builder.commit()

        for fid in fingers:
            _builder.up(fid)

        _builder.publish(self.connection)

    def swift_press(self, points, fingers, pressure=100):
        """
        tap on screen, with pressure
        :param points: [(x1, y1)] 或 (x1, y1)
        :param fingers: 对应的手指编号
        :param pressure: 暂时无用
        """
        if len(points) == 0:
            return
        points = self._check_list(points)
        fingers = self._check_list(fingers)
        points = [list(map(int, point)) for point in points]  # point的坐标必须是int

        _builder = CommandBuilder()
        # 按下down
        for ((x, y), fid) in zip(points, fingers):
            _builder.down(fid, x, y, pressure)
        _builder.commit()

        _builder.publish(self.connection)

    def swift_release(self, fingers):
        if len(fingers) == 0:
            return
        fingers = self._check_list(fingers)
        _builder = CommandBuilder()

        for fid in fingers:
            _builder.up(fid)

        _builder.publish(self.connection)

    def swift_move(self, points, fingers, pressure=100):
        if len(points) == 0:
            return
        points = self._check_list(points)
        fingers = self._check_list(fingers)

        _builder = CommandBuilder()

        for ((x, y), fid) in zip(points, fingers):
            _builder.move(fid, x, y, pressure)

        _builder.publish(self.connection)


@contextmanager
def safe_device(device_id):
    """ use MNTDevice safely """
    _device = MNTDevice(device_id)
    try:
        yield _device
    finally:
        time.sleep(config.DEFAULT_DELAY)
        _device.stop()


if __name__ == "__main__":
    pass
    # _DEVICE_ID = '127.0.0.1:62001'
    #
    # with safe_connection(_DEVICE_ID) as d:
    #     builder = CommandBuilder()
    #     builder.down(0, 400, 400, 50)
    #     builder.commit()
    #     builder.move(0, 500, 500, 50)
    #     builder.commit()
    #     builder.move(0, 800, 400, 50)
    #     builder.commit()
    #     builder.up(0)
    #     builder.commit()
    #     builder.publish(d)
    #
    # with safe_device(_DEVICE_ID) as d:
    #     builder = CommandBuilder()
    #     builder.down(0, 400, 400, 50)
    #     builder.commit()
    #     builder.move(0, 500, 500, 50)
    #     builder.commit()
    #     builder.move(0, 800, 400, 50)
    #     builder.commit()
    #     builder.up(0)
    #     builder.commit()
    #     builder.publish(d.connection)
    #
    # # option1:
    # device = MNTDevice(_DEVICE_ID)
    # device.tap([(400, 500), (500, 500)], duration=1000)
    #
    # # you should control time delay by yourself
    # # otherwise when connection lost, action will never stop.
    # time.sleep(1)
    #
    # device.stop()
    #
    # # option2:
    # with safe_device(_DEVICE_ID) as device:
    #     device.tap([(400, 500), (500, 500)])
    #     device.swipe([(400, 500), (500, 500)], duration=500)
    #     time.sleep(0.5)
