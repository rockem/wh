import pytest

from tests.app_driver import AppDriver, AppError


@pytest.fixture
def app():
    app = AppDriver('http://localhost:8080')
    app.start()
    yield app
    app.stop()


def test_fail_to_create_order_due_to_stock_shortage(app):
    with pytest.raises(AppError) as e:
        app.create_order_for(['Bread'] * 11)
    assert e.value.reason == AppError.BAD_REQUEST


def test_retrieve_tasks_for_order(app):
    app.create_order_for(['Milk'])
    app.next_tasks_contains(
        {'action': 'move', 'destination': [1, 5]},
        {'action': 'pick', 'product': 'Milk'},
        {'action': 'move', 'destination': [0, 0]},
        {'action': 'drop'})


def test_stock_changes_on_dispatched_order(app):
    app.create_order_for(['Salt'])
    assert app.quantity_of('Salt') == 10
    app.complete_all_tasks()
    assert app.quantity_of('Salt') == 9


def test_retrieve_supply_tasks(app):
    app.create_supply_order_for(['Milk', 'Pasta'])
    app.next_tasks_contains(
        {'action': 'move', 'destination': [1, 5]},
        {'action': 'drop', 'product': 'Milk'},
        {'action': 'move', 'destination': [9, 2]},
        {'action': 'drop', 'product': 'Pasta'},
        {'action': 'move', 'destination': [0, 0]})
