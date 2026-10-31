"""Switch repeatedly before, during and after all numerical operations."""
import copy
import io
import threading
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from core.simulation import simulate
from core.network import calculate_cpm
from core.risk_portrait import build_risk_portrait
from ui_wait import settle

ROOT = Path(__file__).resolve().parents[1]
class Upload(io.BytesIO):
    name = 'retention.xlsx'


def switch(app, count=6):
    for i in range(count):
        previous = app.selectbox(key='ui_language').value
        app.selectbox(key='ui_language').set_value('pt_BR' if previous == 'en' else 'en').run()
        assert not app.exception, app.exception


def frames(expected, actual):
    for key in expected:
        pd.testing.assert_frame_equal(expected[key], actual[key], check_exact=True)


def gated_run(app, slot, button_key, target, original):
    entered, release = threading.Event(), threading.Event()
    calls = []
    def guarded(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    def pause_after_cpm(*args, **kwargs):
        calculated = calculate_cpm(*args, **kwargs)
        if not entered.is_set():
            # Pause inside real numerical work, after one iteration's CPM.
            entered.set()
            assert release.wait(90), 'test worker was not released'
        return calculated
    with patch(target, side_effect=guarded), patch('core.simulation.calculate_cpm', side_effect=pause_after_cpm):
        try:
            app.button(key=button_key).click().run()
            assert entered.wait(10)
            job = app.session_state['_jobs'][slot]
            switch(app)
            assert app.session_state['_jobs'][slot] is job
            assert len(calls) == 1, 'language switch restarted numerical work'
            assert app.session_state['_workbook']['content'] == payload
            assert app.session_state['_controls']['widget_99_11'] == 100
            assert app.session_state['_controls']['widget_100_5'] == 73
            assert app.session_state['_controls']['network_diagram_type'] == 'AOA'
        finally:
            release.set()
        settle(app)
        assert len(calls) == 1

payload = (ROOT/'project_risk_template_v2_2.xlsx').read_bytes()
with patch('streamlit.file_uploader', return_value=Upload(payload)) as uploader:
    app = AppTest.from_file(str(ROOT/'app2_2.py'), default_timeout=120).run()
    app.number_input(key='widget_99_11').set_value(100).run()
    app.number_input(key='widget_100_5').set_value(73).run()
    app.selectbox(key='network_diagram_type').set_value('AOA').run()
    # Simulate a widget missing on a UI rerun without a native remove event.
    uploader.return_value = None
    switch(app)
    assert app.number_input(key='widget_99_11').value == 100
    assert app.number_input(key='widget_100_5').value == 73
    gated_run(app, 'simulation', 'widget_102_3', 'core.simulation.simulate', simulate)
    baseline = copy.deepcopy(app.session_state['result'])
    # A language rerun retains identical result objects/data, not a new sample.
    source = app.session_state['_workbook']
    from data_io.model_adapter import to_model_objects
    activities, risks, mappings = to_model_objects(source['data'])
    frames(simulate(activities, risks, mappings, 100, 73), baseline)
    app.selectbox(key='widget_164_18').set_value(activities[-1]['id']).run()
    gated_run(app, 'portrait', 'widget_188_3', 'core.risk_portrait.build_risk_portrait', build_risk_portrait)
    portrait = copy.deepcopy(app.session_state['portrait'])
    app.checkbox(key='widget_197_15').uncheck().run()
    rid = app.selectbox(key='widget_217_11').value
    app.slider(key=f'p_{rid}').set_value(.23).run()
    app.number_input(key=f'dm_{rid}').set_value(.45).run()
    app.number_input(key=f'cm_{rid}').set_value(.65).run()
    gated_run(app, 'treatment', 'widget_235_16', 'core.simulation.simulate', simulate)
    comparison = copy.deepcopy(app.session_state['treatment'])
    switch(app)
    frames(baseline, app.session_state['result'])
    pd.testing.assert_frame_equal(portrait[0], app.session_state['portrait'][0], check_exact=True)
    for key in portrait[1]: frames(portrait[1][key], app.session_state['portrait'][1][key])
    pd.testing.assert_frame_equal(comparison[1], app.session_state['treatment'][1], check_exact=True)
    frames(comparison[0], app.session_state['treatment'][0])
    assert app.selectbox(key='widget_164_18').value == activities[-1]['id']
    assert app.checkbox(key='widget_197_15').value is False
    # Conditional widget cleanup must not erase hidden risk edits/selections.
    app.radio(key='widget_211_5').set_value('Multiple Risks').run()
    others = [r['id'] for r in risks if r['id'] != rid and r.get('active', True)]
    app.multiselect(key='widget_217_81').set_value(others[:1]).run()
    switch(app, 2)
    app.multiselect(key='widget_217_81').set_value([rid]).run()
    assert app.slider(key=f'p_{rid}').value == .23
    assert app.number_input(key=f'dm_{rid}').value == .45
    assert app.number_input(key=f'cm_{rid}').value == .65
    app.radio(key='widget_211_5').set_value('Single Risk').run()
    assert app.selectbox(key='widget_217_11').value == rid
    assert app.slider(key=f'p_{rid}').value == .23
    app.radio(key='widget_211_5').set_value('Multiple Risks').run()
    assert app.multiselect(key='widget_217_81').value == [rid]
    assert not app.exception, app.exception
    # A genuinely different workbook clears all project-specific results.
    uploader.return_value = Upload((ROOT/'examples/irrigation_case_en.xlsx').read_bytes())
    app.run()
    assert 'result' not in app.session_state
    assert 'portrait' not in app.session_state
    assert 'treatment' not in app.session_state
    assert not app.exception, app.exception
print('test_session_retention: PASS (32 repeated switches; all three jobs; hidden edits; exact results)')
