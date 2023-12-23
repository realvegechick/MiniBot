import logging

def log_creator(log_name = 'my_logger'):
    # 创建一个日志记录器
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    # 创建一个处理程序将日志记录到文件
    file_handler = logging.FileHandler('test.log',encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 创建一个处理程序将日志消息输出到命令行
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建一个格式化器，定义日志消息的格式
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 为处理程序设置格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理程序添加到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


if __name__ == "__main__":
    pass