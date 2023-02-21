from nauvus.users.models import Address


def test_get_state_abbreviation():
    abbrev = "GA"
    name1 = "Florida"
    name2 = "California"
    name3 = "This Should Error"

    result = Address.get_state_abbreviation(abbrev)

    assert result == "GA"

    result = Address.get_state_abbreviation(name1)

    assert result == "FL"

    result = Address.get_state_abbreviation(name2)

    assert result == "CA"

    result = Address.get_state_abbreviation(name3)

    assert result is None
