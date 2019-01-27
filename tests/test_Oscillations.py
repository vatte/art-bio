from physiology.Oscillations import Oscillations

def test_Oscillations():
    eeg = Oscillations(100, 1, 256, 0.5, {
        'alpha': [8, 13]
    })

    res = eeg.add_data([[0, 0, 0, 0, 0, 0]])
    assert res == None

    more_data = [[1 for _ in range(250)]]
    res = eeg.add_data(more_data)
    assert res['alpha'] == [-10650.084320520564]
