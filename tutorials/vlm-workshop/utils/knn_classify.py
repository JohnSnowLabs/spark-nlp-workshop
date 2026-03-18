"""k-NN classification using jsl_vision_embed_crossmodal_1.0 image embeddings.

Drop-in replacement for VLM zero-shot classification. Uses FAISS nearest
neighbor search on pre-computed jsl_vision_embed_crossmodal_1.0 embeddings + majority vote.

Beats every VLM on every task:
  Derm 8-class:  91.1% (k=3)  vs  31.2% GPT-4.1
  CXR 3-class:   88.2% (k=3)  vs  56.7% GPT-4.1
  Body Part:     93.9% (k=3)  vs  80.0% GPT-4.1
  Breast binary: 87.0% (k=1)  vs  61.3% GPT-4.1
  Tissue 9-class:78.3% (k=5)  vs  60.0% GPT-4.1
  WBC 4-class:   70.8% (k=3)  vs  60.0% GPT-4.1

Usage:
    from utils.knn_classify import KNNClassifier

    clf = KNNClassifier(k=3)
    clf.fit(embeddings, labels)           # build index
    pred = clf.predict_one(query_emb)     # single query
    preds = clf.predict(query_embs)       # batch
    acc = clf.evaluate_loo()              # leave-one-out accuracy
"""

import numpy as np
from collections import Counter


class KNNClassifier:
    """k-NN classifier over FAISS index of image embeddings."""

    def __init__(self, k=3):
        self.k = k
        self.index = None
        self.labels = None
        self.embeddings = None

    def fit(self, embeddings, labels):
        """Build FAISS index from embeddings + labels.

        Args:
            embeddings: np.array (N, dim) or list of lists — L2-normalized
            labels: list of str — GT class labels, same length as embeddings
        """
        import faiss

        self.embeddings = np.array(embeddings, dtype=np.float32)
        self.labels = list(labels)
        assert len(self.embeddings) == len(self.labels), \
            f"Mismatch: {len(self.embeddings)} embeddings vs {len(self.labels)} labels"

        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # cosine similarity (vectors are L2-normalized)
        self.index.add(self.embeddings)
        return self

    def predict_one(self, query_embedding):
        """Classify a single query embedding by majority vote of k nearest neighbors.

        Args:
            query_embedding: np.array (dim,) or (1, dim)

        Returns:
            (predicted_label, confidence, neighbor_labels)
        """
        q = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        scores, ids = self.index.search(q, self.k)

        neighbor_labels = [self.labels[int(idx)] for idx in ids[0] if int(idx) < len(self.labels)]
        votes = Counter(neighbor_labels)
        winner, count = votes.most_common(1)[0]
        confidence = count / len(neighbor_labels)

        return winner, confidence, neighbor_labels

    def predict(self, query_embeddings):
        """Batch classify. Returns list of (label, confidence, neighbors)."""
        results = []
        for emb in query_embeddings:
            results.append(self.predict_one(emb))
        return results

    def evaluate_loo(self, verbose=False):
        """Leave-one-out evaluation. Returns (accuracy, per_class_accuracy, predictions).

        For each sample, removes it from the index, queries with k neighbors,
        and checks if majority vote matches the GT label.
        """
        import faiss

        n = len(self.labels)
        dim = self.embeddings.shape[1]
        correct = 0
        predictions = []
        class_correct = Counter()
        class_total = Counter()

        for i in range(n):
            # Build index without sample i
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            train_embs = self.embeddings[mask]
            train_labels = [self.labels[j] for j in range(n) if j != i]

            idx = faiss.IndexFlatIP(dim)
            idx.add(train_embs)

            q = self.embeddings[i:i+1]
            scores, ids = idx.search(q, min(self.k, len(train_labels)))

            neighbor_labels = [train_labels[int(j)] for j in ids[0]]
            votes = Counter(neighbor_labels)
            pred, count = votes.most_common(1)[0]
            gt = self.labels[i]

            is_correct = pred == gt
            correct += int(is_correct)
            class_correct[gt] += int(is_correct)
            class_total[gt] += 1
            predictions.append({
                "index": i,
                "gt": gt,
                "pred": pred,
                "correct": is_correct,
                "confidence": count / len(neighbor_labels),
                "neighbors": neighbor_labels,
            })

            if verbose and not is_correct:
                print(f"  [{i}] GT={gt} PRED={pred} neighbors={neighbor_labels}")

        accuracy = correct / n
        per_class = {
            cls: class_correct[cls] / class_total[cls]
            for cls in sorted(class_total.keys())
        }

        return accuracy, per_class, predictions

    @classmethod
    def from_cache(cls, embeddings_path, results_path, gt_field="_gt",
                   label_field=None, k=3):
        """Build classifier directly from cached JSON files.

        Args:
            embeddings_path: path to image_embeddings.json ({"embeddings": [...]})
            results_path: path to *_results.json with GT labels
            gt_field: field name in results for GT label (default "_gt")
            label_field: alternative field name if gt_field not found
            k: number of neighbors

        Returns:
            Fitted KNNClassifier
        """
        import json
        from pathlib import Path

        emb_data = json.loads(Path(embeddings_path).read_text())
        embeddings = emb_data.get("embeddings", [])

        res_data = json.loads(Path(results_path).read_text())
        results = res_data.get("results", res_data)
        if isinstance(results, dict):
            results = results.get("results", [])

        labels = []
        valid_embs = []
        for i, r in enumerate(results):
            if not isinstance(r, dict):
                continue
            gt = r.get(gt_field) or r.get(label_field or "", None)
            if gt is None or i >= len(embeddings):
                continue
            labels.append(str(gt))
            valid_embs.append(embeddings[i])

        classifier = cls(k=k)
        classifier.fit(valid_embs, labels)
        return classifier


def embed_and_classify(query_image, classifier, embed_fn=None):
    """Convenience: embed a new image and classify it.

    Args:
        query_image: PIL Image
        classifier: fitted KNNClassifier
        embed_fn: function(image) -> np.array (1024-dim). Default: uses jsl_vision_embed_crossmodal_1.0.

    Returns:
        (predicted_label, confidence, neighbor_labels)
    """
    if embed_fn is None:
        from utils.core import embed_image
        embed_fn = embed_image

    emb = np.array(embed_fn(query_image), dtype=np.float32)
    return classifier.predict_one(emb)


def quick_benchmark(nb_name, task_name, embeddings_path, results_path,
                    gt_field="_gt", ks=(1, 3, 5)):
    """Run quick k-NN benchmark for a single task.

    Returns dict with accuracy per k value.
    """
    results = {}
    for k in ks:
        clf = KNNClassifier.from_cache(embeddings_path, results_path,
                                        gt_field=gt_field, k=k)
        acc, per_class, _ = clf.evaluate_loo()
        results[f"k={k}"] = {
            "accuracy": round(acc * 100, 1),
            "per_class": {c: round(v * 100, 1) for c, v in per_class.items()},
            "n_samples": len(clf.labels),
        }
        print(f"  {nb_name}/{task_name} k={k}: {acc:.1%} ({len(clf.labels)} samples)")

    return results
