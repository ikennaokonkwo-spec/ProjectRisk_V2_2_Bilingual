"""Language-independent session controls and interrupt-safe numerical jobs.

Workers receive captured inputs and never access Streamlit or localization.
The executor belongs to this browser session; this is not disk persistence.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import streamlit as st

CONTROL_KEYS = {'network_diagram_type', 'widget_99_11', 'widget_100_5',
                'widget_164_18', 'widget_197_15', 'widget_211_5',
                'widget_217_11', 'widget_217_81'}

def keep(widget):
    """Keep canonical widget values even when conditional widgets are removed."""
    def render(*args, **kwargs):
        key = kwargs['key']
        values = st.session_state.setdefault('_controls', {})
        if key not in st.session_state and key in values:
            st.session_state[key] = deepcopy(values[key])
            # Avoid Streamlit's warning about two competing defaults.
            kwargs.pop('value', None)
            kwargs.pop('default', None)
        def remember():
            st.session_state['_controls'][key] = deepcopy(st.session_state[key])
        value = widget(*args, **kwargs, on_change=remember)
        values[key] = deepcopy(value)
        return value
    return render

def reset_project():
    for job in st.session_state.get('_jobs', {}).values():
        job['future'].cancel()  # Running work may finish, but has no commit route.
    st.session_state['_jobs'] = {}
    for key in list(st.session_state):
        if key in CONTROL_KEYS or key.startswith(('p_', 'dm_', 'cm_')) or key in {
            'sig', 'result', 'portrait', 'treatment', 'treatment_specs', '_controls'}:
            st.session_state.pop(key, None)

def upload_changed():
    upload = st.session_state.get('widget_38_9')
    if upload is None:
        reset_project()
        st.session_state.pop('_workbook', None)

def workbook(upload):
    """A language rerun cannot erase the source bytes. Native removal can."""
    if upload is not None:
        content = upload.getvalue()
        digest = hashlib.sha256(content).hexdigest()
        previous = st.session_state.get('_workbook')
        if previous is None or previous['digest'] != digest:
            reset_project()
            st.session_state['_workbook'] = {
                'content': content, 'digest': digest, 'name': upload.name}
    return st.session_state.get('_workbook')

def submit(slot, signature, function, *args, **kwargs):
    jobs = st.session_state.setdefault('_jobs', {})
    if slot in jobs:
        return False
    executor = st.session_state.get('_executor')
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='project-risk')
        st.session_state['_executor'] = executor
    # Core functions are unchanged. Capture arguments once, outside UI reruns.
    baseline = kwargs.pop('baseline_result', None)
    captured_kwargs = deepcopy(kwargs)
    if baseline is not None:
        # The unchanged core reads this completed result without mutation.
        captured_kwargs['baseline_result'] = baseline
    future = executor.submit(function, *deepcopy(args), **captured_kwargs)
    jobs[slot] = {'signature': deepcopy(signature), 'future': future}
    return True

def collect(slot, signature):
    jobs = st.session_state.setdefault('_jobs', {})
    job = jobs.get(slot)
    if job is None:
        return None
    if job['signature'] != signature:
        job['future'].cancel()
        del jobs[slot]
        return None
    if not job['future'].done():
        return None
    # Keep successful completion until all UI-state writes are acknowledged.
    # A language rerun can interrupt any Streamlit Session State assignment.
    # Failures are reported in the main thread and never overwrite saved results.
    try:
        return job['future'].result()
    except Exception as error:
        del jobs[slot]
        from localization import language
        label = 'Falha no cálculo' if language() == 'pt_BR' else 'Calculation failed'
        st.error(f'{label}: {error}')
        return None

def acknowledge(slot):
    st.session_state.get('_jobs', {}).pop(slot, None)

def pending(slot):
    return slot in st.session_state.get('_jobs', {})

@st.fragment(run_every=0.5)
def progress():
    jobs = st.session_state.get('_jobs', {})
    if any(job['future'].done() for job in jobs.values()):
        st.rerun()
    if jobs:
        st.info('Cálculo em andamento. Você pode mudar o idioma.' if st.session_state.get('ui_language') == 'pt_BR'
                else 'Calculation running. You can switch languages.')

def tabs(labels, key):
    """Store the active tab by position, never by its translated label."""
    values = st.session_state.setdefault('_controls', {})
    index = values.get(key, 0)
    st.session_state[key] = labels[index]
    def changed():
        values[key] = labels.index(st.session_state[key])
    return st.tabs(labels, key=key, on_change=changed)

def expander(label, *, key, expanded=False):
    values = st.session_state.setdefault('_controls', {})
    if key not in st.session_state and key in values:
        st.session_state[key] = values[key]
    def changed():
        values[key] = st.session_state[key]
    return st.expander(label, expanded=expanded, key=key, on_change=changed)
