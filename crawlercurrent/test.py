def test():
    count = 0
    while True:
        if count > 10:
            return count
        else:
            count += 1


if __name__ == '__main__':
    print(test())
