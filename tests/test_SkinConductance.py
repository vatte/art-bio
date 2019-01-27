from physiology.SkinConductance import SkinConductance

def test_SkinConductance():
    eda = SkinConductance(100, 20, 0.4, 20)
    res = eda.add_data([0, 0, 0, 0, 0, 0])
    assert res['edr'] == []
