from flask import Flask, jsonify, request, render_template

from system import BloomGuardSystem

app = Flask(__name__)
system = BloomGuardSystem(n_items=500, fp_rate=0.02)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/reset", methods=["POST"])
def api_reset():
    data = request.get_json(silent=True) or {}
    system.reset(
        n_items=data.get("n_items"),
        fp_rate=data.get("fp_rate"),
    )
    return jsonify({"ok": True})


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json(silent=True) or {}
    item = data.get("item", "")
    event = system.add_item(item)
    return jsonify(event)


@app.route("/api/seed", methods=["POST"])
def api_seed():
    data = request.get_json(silent=True) or {}
    count = int(data.get("count", 50))
    ratio = float(data.get("duplicate_ratio", 0.25))
    result = system.seed_random(count=count, duplicate_ratio=ratio)
    return jsonify(result)


@app.route("/api/stats")
def api_stats():
    return jsonify(system.stats())


@app.route("/api/bits")
def api_bits():
    return jsonify(system.bit_array_preview())


@app.route("/api/recent")
def api_recent():
    return jsonify(system.recent())


@app.route("/api/stack")
def api_stack():
    return jsonify(system.stack_trace())


@app.route("/api/graph")
def api_graph():
    return jsonify(system.collision_graph())


@app.route("/api/bst-traversal")
def api_bst_traversal():
    return jsonify(system.bst_traversal())


@app.route("/api/benchmark", methods=["POST"])
def api_benchmark():
    data = request.get_json(silent=True) or {}
    target = data.get("target")
    return jsonify(system.run_benchmark(target=target))


@app.route("/api/greedy", methods=["POST"])
def api_greedy():
    data = request.get_json(silent=True) or {}
    total_budget = int(data.get("total_budget", 300_000))
    chunk_size = int(data.get("chunk_size", 2000))
    return jsonify(system.run_greedy(total_budget=total_budget, chunk_size=chunk_size))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
