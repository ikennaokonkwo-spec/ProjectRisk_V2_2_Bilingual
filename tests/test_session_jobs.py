"""Session ownership, stale completion, failures, removal and layout mapping."""
from concurrent.futures import Future
from unittest.mock import patch
from presentation import session
from io import BytesIO

class Upload(BytesIO): name = 'test.xlsx'
state = {'ui_language': 'pt_BR'}
with patch.object(session.st, 'session_state', state):
    session.workbook(Upload(b'one'))
    state.update(result={'saved': True}, portrait='saved', treatment='saved')
    state['_controls'] = {'dm_R1': .3}
    assert session.workbook(None)['content'] == b'one'
    assert state['result'] == {'saved': True}
    first = Future()
    first.set_running_or_notify_cancel()
    state['_jobs'] = {'simulation': {'signature': ('one',100,42), 'future': first}}
    # Changing real input must invalidate the old running job's commit route.
    session.workbook(Upload(b'two'))
    first.set_result('obsolete result')
    assert session.collect('simulation', ('two',100,42)) is None
    assert 'result' not in state and '_controls' not in state
    assert state['ui_language'] == 'pt_BR'
    state['result'] = 'valid result'
    bad = Future(); bad.set_exception(ValueError('injected failure'))
    state['_jobs'] = {'portrait': {'signature': 1, 'future': bad}}
    with patch.object(session.st, 'error') as error:
        assert session.collect('portrait',1) is None
        assert error.call_count == 1
    assert state['result'] == 'valid result' and not session.pending('portrait')
    assert session.submit('simulation', 1, lambda x: x, 9)
    assert not session.submit('simulation', 1, lambda: 'duplicate')
    state['_jobs']['simulation']['future'].result(timeout=5)
    assert session.collect('simulation',1) == 9
    # A rerun before commit acknowledgement must expose the same completion.
    assert session.collect('simulation',1) == 9
    session.acknowledge('simulation')
    assert not session.pending('simulation')
    state['_executor'].shutdown()
    # Explicit native upload removal is different from a language rerun.
    state['widget_38_9'] = None
    session.upload_changed()
    assert '_workbook' not in state and 'result' not in state
    assert state['ui_language'] == 'pt_BR'
    # Track tab by canonical position through translated labels.
    with patch.object(session.st, 'tabs', return_value=[]) as widget:
        session.tabs(['CDF', 'Frequency'], key='test_tabs')
        state['test_tabs'] = 'Frequency'
        widget.call_args.kwargs['on_change']()
        session.tabs(['Acumulada', 'Frequência'], key='test_tabs')
        assert state['test_tabs'] == 'Frequência'
    with patch.object(session.st, 'expander', return_value=None) as widget:
        session.expander('Input', key='test_expander')
        state['test_expander'] = True
        widget.call_args.kwargs['on_change']()
        state.pop('test_expander')
        session.expander('Entrada', key='test_expander')
        assert state['test_expander'] is True
print('test_session_jobs: PASS')
