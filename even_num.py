def even_num(x):
    lst = []
    for i in range(len(x)):
        if x[i] % 2 == 0:
            lst.append(x[i])
    print(lst)
    return lst

if __name__ == '__main__':
    x = [1,2,3,4,5,6]
    assert even_num(x) == [2,4,6]  