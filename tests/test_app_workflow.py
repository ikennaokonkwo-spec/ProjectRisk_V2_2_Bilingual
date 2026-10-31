"""Exercise upload, simulation, portrait, comparison and stale-result invalidation."""
import io
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from ui_wait import settle
class Upload(io.BytesIO):
    name='project_risk_template_v2_2.xlsx'
upload=Upload(Path('project_risk_template_v2_2.xlsx').read_bytes())
with patch('streamlit.file_uploader',return_value=upload):
    app=AppTest.from_file(str(Path('app2_2.py').resolve()),default_timeout=60).run()
    assert not app.exception,app.exception
    app.number_input[0].set_value(100).run()
    next(b for b in app.button if b.label=='Run simulation').click().run()
    settle(app)
    assert not app.exception,app.exception
    next(b for b in app.button if b.label=='Build complete Risk Portrait').click().run()
    settle(app)
    assert not app.exception,app.exception
    next(b for b in app.button if b.label=='Run treatment comparison').click().run()
    settle(app)
    assert not app.exception,app.exception
    assert 'treatment' in app.session_state
    next(n for n in app.number_input if n.label.startswith('Duration impact multiplier')).set_value(.5).run()
    assert 'treatment' not in app.session_state
    assert not app.exception,app.exception
print('test_app_workflow: PASS')
