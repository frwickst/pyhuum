from huum.const import STATUS_CODE_TEXTS, SaunaStatus


def test_code_texts():
    status_enum_list = list(map(int, SaunaStatus))
    for status_code in status_enum_list:
        assert STATUS_CODE_TEXTS.get(status_code, False)
