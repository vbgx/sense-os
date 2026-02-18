import json
from pathlib import Path

from clustering_worker.pipeline.build_vectors import build_vectors
from clustering_worker.clustering.merge import cluster_vectors


def _load_fixture():
    p = Path("tests/fixtures/clustering/golden/vertical_1_sample_50.json")
    return json.loads(p.read_text(encoding="utf-8"))


def test_golden_snapshot_clustering_is_stable():
    fx = _load_fixture()
    job = {"vertical_db_id": fx["vertical_db_id"], "taxonomy_version": fx["taxonomy_version"]}
    instances = fx["instances"]

    instance_ids, vectors, _ = build_vectors(job, instances)

    params = {"min_cluster_size": 4, "min_samples": 2, "metric": "euclidean"}
    clusters = cluster_vectors(vectors, params=params)

    snapshot = {
        "vertical_db_id": fx["vertical_db_id"],
        "taxonomy_version": fx["taxonomy_version"],
        "n_instances": len(instance_ids),
        "params": params,
        "assignments": {str(iid): int(clusters[idx]) for idx, iid in enumerate(instance_ids)},
    }

    snap_path = Path("tests/fixtures/clustering/golden/vertical_1_snapshot.json")
    if not snap_path.exists():
        snap_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
        assert False, "snapshot created; re-run test"
    else:
        expected = json.loads(snap_path.read_text(encoding="utf-8"))
        assert snapshot == expected
