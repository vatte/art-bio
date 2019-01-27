from physiology.HeartRate import HeartRate

def test_HeartRate():
    ecg = HeartRate(100, 20)
    res = ecg.add_data([0, 0, 0, 0, 0, 0])
    assert res['ibi'] == []
