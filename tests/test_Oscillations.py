from physiology.Oscillations import Oscillations

def test_Oscillations():
    eeg = Oscillations(100, 1, 256, 0.5, {
        'alpha': [8, 13]
    })

    res = eeg.add_data([[0], [0], [0], [0], [0], [0]])
    assert res == None

    more_data = [[1] for _ in range(250)]
    res = eeg.add_data(more_data)
    assert res['alpha'] == [-10650.084320520564]


def test_Oscillations_10Hz():
    sin_10 = [[50], [79] ,[98] ,[98] ,[79] ,[50] ,[21] ,[2] ,[2] ,[21] ]
    wave = []
    for _ in range(30):
        wave += sin_10
    
    eeg = Oscillations(100, 1, 256, 0.5, {
        'alpha': [8, 13],
        'beta': [13, 30]
    })
    res = eeg.add_data(wave)
    print(res)

import numpy as np

def test_Oscillations_5Hz():
    sin_5 = [[50], [98] ,[79] ,[21] ,[2] ]
    wave = []
    for _ in range(60):
        wave += sin_5
    wave = np.array(wave) * 100
    
    eeg = Oscillations(100, 1, 256, 0.5, {
        'all': [1, 40],
        'alpha': [8, 13],
        'beta': [4.9, 5.1]
    })
    res = eeg.add_data(wave)
    print(res)

