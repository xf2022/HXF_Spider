import concurrent.futures
import threading
import time


# 示例任务函数
def task(n):
    print(f"Task {n} started id {threading.current_thread()}")
    time.sleep(2)  # 模拟任务耗时
    print(f"Task {n} completed")
    return n


# 使用线程池执行任务
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 提交任务
        future_to_task = {executor.submit(task, i): i for i in range(10)}

        # 等待所有任务完成
        for future in concurrent.futures.as_completed(future_to_task):
            task_num = future_to_task[future]
            try:
                result = future.result()
                print(f"Task {task_num} result: {result}")
            except Exception as exc:
                print(f"Task {task_num} generated an exception: {exc}")


if __name__ == "__main__":
    main()