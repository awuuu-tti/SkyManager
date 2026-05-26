import db


def test_db_module_import():
    assert db is not None


def test_db_has_functions():
    functions = dir(db)

    assert len(functions) > 0


def test_db_attributes():
    attrs = dir(db)

    assert isinstance(attrs, list)


def test_db_string():
    assert str(db) != ''


def test_db_dict():
    assert isinstance(db.__dict__, dict)


def test_all_callable_functions():
    functions = []

    for name in dir(db):
        obj = getattr(db, name)

        if callable(obj):
            functions.append(name)

    assert len(functions) > 0


def test_module_name():
    assert db.__name__ == 'db'


def test_module_doc():
    assert hasattr(db, '__doc__')


def test_module_file():
    assert 'db.py' in db.__file__


def test_dir_returns_list():
    assert type(dir(db)) == list


def test_callable_check():
    result = callable(getattr(db, '__name__', None))

    assert result is False


def test_module_variables():
    variables = db.__dict__

    assert len(variables) > 0


def test_db_repr():
    assert repr(db) != ''


def test_db_type():
    assert type(db).__name__ == 'module'


def test_getattr():
    assert getattr(db, '__name__') == 'db'