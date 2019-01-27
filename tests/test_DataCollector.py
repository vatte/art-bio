from physiology.DataCollector import DataCollector

def test_DataCollector():
    dc = DataCollector(100)
    res = dc.add_data([0, 0, 0, 0, 0, 0])
    assert res['feature'] == []
