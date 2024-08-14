import multiprocessing

print('子进程的列表：{}'.format(multiprocessing.active_children()))
print('电脑的CPU数量：{}'.format(multiprocessing.cpu_count()))
print('现在运行的进程：{}'.format(multiprocessing.current_process()))