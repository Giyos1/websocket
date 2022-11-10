# import asyncio
# import time
# import random
# from threading import Thread
# from enum import Enum, auto
# import heapq
# import sys
#
#
# def random_delay():
#     return random.random() * 5
#
#
# def random_countdown():
#     return random.randrange(5)
#
#
# def launch_rocket(delay, countdown):
#     time.sleep(delay)
#     for i in reversed(range(countdown)):
#         print(f"{i + 1}...")
#         time.sleep(1)
#     print('rocket lunched !!')
#
#
# class State(Enum):
#     WAITING = auto()
#     COUNTING = auto()
#     LAUNCHING = auto()
#
#
# class Op(Enum):
#     WAIT = auto()
#     STOP = auto()
#
#
# class Launch:
#     def __init__(self, delay, countdown):
#         self._state = State.WAITING
#         self._delay = delay
#         self._countdown = countdown
#
#     def step(self):
#         if self._state is State.WAITING:
#             return Op.WAIT, self._delay
#         if self._state is State.COUNTING:
#             if self._countdown == 0:
#                 self._state = State.LAUNCHING
#             else:
#                 print(f'{self._countdown}...')
#                 self._countdown -= 1
#                 return Op.WAIT, 1
#         if self._state is State.LAUNCHING:
#             print('Rocket launched!')
#             return Op.STOP, None
#
#         assert False, self._state
#
#
# def now():
#     return time.time()
#
#
# def run_fsm(rockets):
#     start = now()
#     work = [(start, i, Launch(d, c)) for i, (d, c) in enumerate(rockets)]
#
#     while work:
#         step_at, id, launch = heapq.heappop(work)
#         wait = step_at - now()
#
#         if wait > 0:
#             time.sleep(wait)
#
#         op, arg = launch.step()
#
#         if op is Op.WAIT:
#             step_at = now() + arg
#             heapq.heappush(work, (step_at, id, launch))
#         else:
#             assert op is Op.STOP
#
#
# def rockets():
#     N = 10_000
#     return [
#         (random_delay(), random_countdown())
#         for _ in range(N)
#     ]
#
#
# def run_threads():
#     threads = [Thread(target=launch_rocket, args=(d, c))
#                for d, c in rockets()]
#
#     for thread in threads:
#         thread.start()
#
#     for thread in threads:
#         thread.join()
#
#
# if __name__ == '__main__':
#     # for d, c in rockets():
#     #     launch_rocket(d, c)
#
#     # run_threads()
#
#     # run_fsm(rockets())
#     import os
#     from time import sleep
#     from threading import Thread
#
#     threads = [
#         Thread(target=lambda: sleep(60)) for i in range(10000)]
#
#     [t.start()
#      for t in threads]
#     print(f'PID = {os.getpid()}')
#
#     [t.join()
#      for t in threads]
# from models import get_audio
#
#
# async def execute(text):
#     result = get_audio(text)


# async def main():
#     # Using asyncio.create_task() method to run coroutines concurrently as asyncio
#     task1 = asyncio.create_task(
#         execute(2, 'hello'))
#
#     task2 = asyncio.create_task(
#         execute(1, 'world'))
#
#     print(f"started at {time.strftime('%X')}")
#
#     # Wait until both tasks are completed (should take
#     # around 2 seconds.)
#     await task1
#     await task2
#
#     print(f"finished at {time.strftime('%X')}")
#
#
# def execute2(delay, value):
#     time.sleep(delay)
#     print(value)
#
#
# def main2():
#     # Using asyncio.create_task() method to run coroutines concurrently as asyncio
#     print(f"started at {time.strftime('%X')}")
#     task1 = execute2(2, 'hello')
#
#     task2 = execute2(1, 'world')
#
#     # Wait until both tasks are completed (should take
#     # around 2 seconds.)
#
#     print(f"finished at {time.strftime('%X')}")
#
#
# asyncio.run(main())

# # main2()
# from models import get_audio
# import asyncio
#
# # async def main(text):
# #     list1 = []
# #     x = text.split()
# #     for _ in x:
# #         task1 = loop.create_task(get_audio(_))
# #         list1.append(task1)
# #
# #     await asyncio.wait(list1)
#
# import asyncio
#
#
# async def async_func(text):
#     print(get_audio(text))
#
#
# async def main():
#     taskA = loop.create_task(async_func('taskA'))
#     taskB = loop.create_task(async_func('taskB'))
#     taskC = loop.create_task(async_func('taskC'))
#     await asyncio.wait([taskA, taskB, taskC])


# if __name__ == "__main__":
#     try:
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(main())
#     except:
#         pass

# if __name__ == "__main__":
#     try:
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(main("Assalomu Alleykum Valeykum Assalom hdsa Ulu"))
#     except:
#         pass
# def romanToInt(s):
#     """
#     :type s: str
#     :rtype: int
#     """
#     dict = {'I': 1,
#             'V': 5,
#             'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000, }
#     a = 0
#     for i in range(len(s)):
#         if i + 1 == len(s):
#             a += (dict[s[i]])
#             return a
#         if dict[s[i]] < dict[s[i + 1]]:
#             print(f'{a}-{dict[s[i]]}')
#             a -= dict[s[i]]
#             print(a)
#         else:
#             a += dict[s[i]]
#
#
# if __name__ == '__main__':
#     print(romanToInt("MCMXCIV"))
