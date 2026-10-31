def settle(app):
    for _ in range(5):
        jobs = dict(app.session_state['_jobs']) if '_jobs' in app.session_state else {}
        if not jobs:
            break
        for job in jobs.values():
            job['future'].result(timeout=120)
        app.run()
    assert not app.exception, app.exception
    return app
