def rdt_nums(train_ratio, dev_ratio, test_ratio, len_seq):
    ''' num_train is left except dev and train from len_seq. '''
    # Calc ratios.
    total = train_ratio + dev_ratio + test_ratio
    r = train_ratio / total
    d = dev_ratio / total
    t = test_ratio / total
    # Calc nums.
    n_train = int(len_seq * train_ratio / total)
    n_dev = int(len_seq * dev_ratio / total)
    n_test = len_seq - n_train - n_dev
    return (n_train, n_dev, n_test)

def rdt_partition(n_train, n_dev, n_test, datums):
    ''' Item of datums is datum of dataset. '''
    assert len(datums) == n_train + n_dev + n_test
    
    train = datums[:n_train]
    dev = datums[n_train: n_train + n_dev]
    test = datums[n_train + n_dev:]
    return train, dev, test
