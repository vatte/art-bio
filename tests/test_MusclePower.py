from physiology.MusclePower import MusclePower

def test_MusclePower():
    emg = MusclePower(100)
    res = emg.add_data([0, 0, 0, 0, 0, 0])
    assert res['power'] == [0]
    res = emg.add_data([-1, 1, -1, 1, -1, 1])
    assert res['power'] == [1]
