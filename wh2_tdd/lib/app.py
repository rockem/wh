import json

from bottle import run, get, post, request, abort, response, put

from lib import stock, orders, task_factory, tasks, task_actions
from lib.stock import StockAllocationError


@get('/health')
def health():
    return json.dumps({'status': 'UP'})


@post('/orders')
def create_order():
    order_items = json.loads(request.body.read())
    _allocate_stock_for(order_items)
    orders.add_order(order_items)
    response.status = 201


def _allocate_stock_for(order_items):
    try:
        stock.allocate_items(order_items)
    except StockAllocationError:
        abort(code=400, text='stock allocation error')


@post('/supply')
def create_supply():
    order_items = json.loads(request.body.read())
    orders.add_supply(order_items)
    response.status = 201


@get('/next-tasks')
def get_next_tasks():
    tasks.add_all(task_factory.create_tasks_for(orders.get_orders()))
    response.content_type = 'application/json'
    return json.dumps([t.__dict__ for t in tasks.next_tasks()])


@put('/tasks/<id>/complete')
def complete_task(id):
    task_actions.on_task_complete(tasks.get(id))


@get('/stock')
def get_stock():
    return json.dumps(stock.all())


run(host='localhost', port=8080, debug=True)
