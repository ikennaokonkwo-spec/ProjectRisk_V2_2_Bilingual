"""Full workflows in both workbook languages, with state-preserving switches."""
import copy,io
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
class Upload(io.BytesIO):name='input.xlsx'
for template,initial in [('project_risk_template_v2_2.xlsx','en'),('project_risk_template_v2_2_pt_BR.xlsx','pt_BR')]:
    with patch('streamlit.file_uploader',return_value=Upload((ROOT/template).read_bytes())):
        app=AppTest.from_file(str(ROOT/'app2_2.py'),default_timeout=120).run()
        if initial=='pt_BR':app.selectbox(key='ui_language').set_value('pt_BR').run()
        assert not app.exception,app.exception
        app.number_input[0].set_value(100).run()
        next(b for b in app.button if b.label in ('Run simulation','Executar simulação')).click().run()
        assert not app.exception,app.exception
        next(b for b in app.button if b.label in ('Build complete Risk Portrait','Construir retrato completo de riscos')).click().run()
        assert not app.exception,app.exception
        next(b for b in app.button if b.label in ('Run treatment comparison','Executar comparação de tratamento')).click().run()
        assert not app.exception,app.exception
        result=copy.deepcopy(app.session_state['result'])
        comparison=copy.deepcopy(app.session_state['treatment'][1])
        specs=copy.deepcopy(app.session_state['treatment_specs'])
        portrait=copy.deepcopy(app.session_state['portrait'][0])
        for language in (('pt_BR','en') if initial=='en' else ('en','pt_BR')):
            app.selectbox(key='ui_language').set_value(language).run()
            assert not app.exception,app.exception
            for key in result:pd.testing.assert_frame_equal(result[key],app.session_state['result'][key],check_exact=True)
            pd.testing.assert_frame_equal(comparison,app.session_state['treatment'][1],check_exact=True)
            pd.testing.assert_frame_equal(portrait,app.session_state['portrait'][0],check_exact=True)
            assert specs==app.session_state['treatment_specs']
            expected='4. Project Risk Results' if language=='en' else '4. Resultados dos riscos do projeto'
            assert expected in [h.value for h in app.header]
        next(n for n in app.number_input if 'Duration impact multiplier' in n.label or 'Multiplicador do impacto na duração' in n.label).set_value(.5).run()
        assert 'treatment' not in app.session_state
        assert 'portrait' in app.session_state
        assert not app.exception,app.exception
        app.radio[0].set_value('Multiple Risks').run()
        assert len(app.multiselect)==1
        next(b for b in app.button if b.label in ('Run treatment comparison','Executar comparação de tratamento')).click().run()
        assert not app.exception,app.exception
        assert len(app.session_state['treatment_specs'])==2
        print(template,'upload/simulation/portrait/single+multiple treatment/language-switch: PASS',flush=True)
print('test_bilingual_workflow: PASS')
