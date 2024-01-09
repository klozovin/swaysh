from signal import signal, pause, SIGUSR1, SIGUSR2, SIGRTMIN


def sigusr1_handler(signal_num: int, b):
    print(f"SIGUSR1: {signal_num}, {b}")


def sigusr2_handler(signal_num: int, b):
    print(f"SIGUSR2: {signal_num}, {b}")


def sigrt_handler(signal_num: int, b):
    print(f"SIGRT: {signal_num}, {b}")


def main():
    signal(SIGUSR1, sigusr1_handler)
    signal(SIGUSR2, sigusr2_handler)
    signal(SIGRTMIN+1, sigrt_handler)

    while True:
        print("Waiting for signal...")
        pause()


if __name__ == "__main__":
    main()