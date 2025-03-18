# def longestPalindrome(s: str) -> str:
#
#     str_list = list(s)
#
#     res_dic = {}
#     result = str_list[0]
#
#     def is_palindrome(lst: list):
#         left_1 = 0
#         right_1 = len(lst) - 1
#
#         print(f'传入的列表{lst}')
#
#         while True:
#             if right_1 - left_1 <= 1:
#                 return True
#             if lst[right_1] == lst[left_1]:
#                 left_1 += 1
#                 right_1 -= 1
#                 continue
#             else:
#                 return False
#
#     left = 0
#
#     while True:
#         right = len(s) - 1
#
#         if right <= left:
#             break
#
#         print(right, left, 'waiceng')
#
#         while True:
#             if right <= left:
#                 break
#             print(right, left, '内层1')
#             if str_list[right] != str_list[left]:
#                 right -= 1
#                 continue
#
#
#             if is_palindrome(str_list[left + 1 : right]):
#                 str_pal = ''.join(str_list[left: right + 1])
#                 res_dic[str_pal] = right - left + 1
#                 right -= 1
#                 break
#             else:
#                 right -= 1
#         left += 1
#
#     num = 0
#
#     for value in res_dic:
#         if res_dic[value] > num:
#             num = res_dic[value]
#             result = value
#
#     return result
#
#
# print(longestPalindrome('caba'))
#
# from threading import (Thread, Event)
# event = Event()
#
#
# def test(num):
#     if num & 1:
#         for i in range(0, 100000, 2):
#             if i == 50002:
#                 event.set()
#             print(i)
#     else:
#         for i in range(1, 100000, 2):
#             event.wait()
#             print(i)
#
#
# t1 = Thread(target= test, args=(1,))
# t2 = Thread(target= test, args=(0,))
#
#
# t1.start()
# t2.start()





