from flask import Flask, jsonify, request
import numpy as np
import re
import pulp as pl

app = Flask(__name__)

g_dungeons = np.loadtxt('cols.csv', dtype=str, encoding='utf8')
g_monsters = np.loadtxt('rows.csv', dtype=str, encoding='utf8')
g_matrix = np.genfromtxt('matrix.csv', delimiter=',')


@app.route("/")
def hello_world():
    return app.send_static_file('index.html')


@app.route("/dungeons", methods=['Get'])
def get_dungeons():
    global g_dungeons
    return jsonify(g_dungeons.tolist())


@app.route("/monsters", methods=['Get'])
def get_monsters():
    global g_monsters
    return jsonify(g_monsters.tolist())


@app.route("/computation", methods=['Post'])
def computation():
    request_data = request.get_json()
    filter_enum = request_data['filter']
    low_level_idx = request_data['lowLevel']
    target_dict = request_data['target']

    global g_monsters, g_dungeons, g_matrix
    # filter dungeons and matrix
    filtered_dungeons, filtered_matrix = __filter_dungeons(g_dungeons, g_matrix, filter_enum, low_level_idx)
    # filter monster and matrix
    filtered_monsters, filtered_matrix = __filter_monsters(g_monsters, filtered_matrix, target_dict)
    # order target monster
    ordered_target_amount = np.array([target_dict.get(x) for x in filtered_monsters])
    # filter empty dungeons
    filtered_dungeons, filtered_matrix = __filter_empty_dungeons(filtered_dungeons, filtered_matrix)
    # compute
    status, play_times, minimal = __do_pure_integer_programming(filtered_matrix,
                                                                ordered_target_amount.reshape(filtered_matrix.shape[0],
                                                                                              1))
    resp = __encode_resp(play_times, filtered_matrix, filtered_dungeons, filtered_monsters, status, minimal)
    return jsonify(resp)


def __encode_resp(play_times: np.ndarray, matrix: np.ndarray, dungeons: np.ndarray, monsters: np.ndarray,
                  status: int, minimal: int) -> dict:
    dungeon_idx = np.where(play_times > 0)
    result_matrix = matrix[:, dungeon_idx[0]].tolist()
    result_dungeons = dungeons[dungeon_idx[0]].tolist()
    result_play_times = play_times[dungeon_idx[0]].tolist()
    result_monster = monsters.tolist()
    return {
        'status': status,
        'matrix': result_matrix,
        'monsters': result_monster,
        'dungeons': result_dungeons,
        'playTimes': result_play_times,
        'minimal': minimal,
    }


def __do_pure_integer_programming(a: np.ndarray, b: np.ndarray) -> (int, np.ndarray, int):
    eps = 1e-3
    # Variables
    x = np.array([pl.LpVariable("x" + str(i), lowBound=0, upBound=15, cat='Integer') for i in range(a.shape[1])],
                 dtype=object)
    # Problem
    prob = pl.LpProblem("prob", pl.LpMinimize)
    # Objective
    prob += np.sum(x)
    # Constraints
    for row in range(a.shape[0]):
        prob += np.dot(a[row], x) >= b[row]
    prob += np.sum(x) >= eps  # forbid zero-vector

    # Solve
    status = prob.solve()
    play_times = np.array([x_.varValue for x_ in x]) if status == 1 else np.array([])
    minimal = pl.value(prob.objective) if status == 1 else -1
    return status, play_times, minimal


def __filter_empty_dungeons(dungeons: np.ndarray, matrix: np.ndarray) -> (np.ndarray, np.ndarray):
    filter_idx = np.where(np.all(matrix == 0, axis=0) == False)
    filtered_dungeons = dungeons[filter_idx[0]]
    filtered_matrix = matrix[:, filter_idx[0]]
    return filtered_dungeons, filtered_matrix


def __filter_monsters(monster: np.ndarray, matrix: np.ndarray, target_dict: dict) -> (np.ndarray, np.ndarray):
    target_monsters = np.array(list(target_dict.keys()))
    filter_idx = np.where(np.isin(monster, target_monsters) == True)
    filtered_matrix = matrix[filter_idx[0], :]
    filtered_monsters = monster[filter_idx[0]]
    return filtered_monsters, filtered_matrix


def __filter_dungeons(dungeons: np.ndarray, matrix: np.ndarray, filter_enum: int = 7, low_level_idx: int = 5) -> (
        np.ndarray, np.ndarray):
    boss_filter = __cols_boss_filter(dungeons) if filter_enum & 1 == 1 \
        else np.zeros(dungeons.shape, dtype=bool)
    monster_filter = __cols_monster_filter(dungeons) if (filter_enum >> 1) & 1 == 1 \
        else np.zeros(dungeons.shape, dtype=bool)
    level_filter = __cols_level_filter(dungeons, low_level_idx) if (filter_enum >> 2) & 1 == 1 \
        else np.zeros(dungeons.shape, dtype=bool)

    total_filter = np.logical_or(np.logical_or(boss_filter, monster_filter), level_filter)
    filter_idx = np.where(total_filter == False)
    filtered_dungeons = dungeons[filter_idx[0]]
    filtered_matrix = matrix[:, filter_idx[0]]
    return filtered_dungeons, filtered_matrix


def __cols_boss_filter(dungeons: np.ndarray) -> np.ndarray:
    boss_reg = re.compile(r'.*：首领$')
    boss_match = np.vectorize(lambda x: bool(boss_reg.match(x)))
    return boss_match(dungeons)


def __cols_monster_filter(dungeons: np.ndarray) -> np.ndarray:
    monster_reg = re.compile(r'^妖气封印')
    monster_match = np.vectorize(lambda x: bool(monster_reg.match(x)))
    return monster_match(dungeons)


def __cols_level_filter(dungeons: np.ndarray, idx: int) -> np.ndarray:
    level_reg = re.compile(fr'.*[^御魂]第([{idx}-9]|10)层$')
    level_match = np.vectorize(lambda x: bool(level_reg.match(x)))
    return level_match(dungeons)


if __name__ == '__main__':
    app.run(port=8765, debug=True)
