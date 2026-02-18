import inspect
import trend_worker.metrics as metrics_pkg


def test_metrics_do_not_import_raw_modules():
    forbidden = ["load_clusters", "signals", "pain_instances"]

    for name in dir(metrics_pkg):
        module = getattr(metrics_pkg, name)
        if not hasattr(module, "__file__"):
            continue

        src = inspect.getsource(module)
        for f in forbidden:
            assert f not in src
