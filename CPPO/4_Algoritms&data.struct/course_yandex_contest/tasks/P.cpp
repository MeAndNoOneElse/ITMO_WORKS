#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;
int n;
vector<vector<int>> w;
bool stronglyConnected(int C) {
    vector<vector<int>> adj(n), radj(n);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i != j && w[i][j] <= C) {
                adj[i].push_back(j);
                radj[j].push_back(i);
            }
        }
    }
    vector<bool> visited(n, false);
    auto dfs = [&](int v, const vector<vector<int>>& graph, auto&& self) -> void {
        visited[v] = true;
        for (int to : graph[v]) {
            if (!visited[to]) {
                self(to, graph, self);
            }
        }
    };
    dfs(0, adj, dfs);
    for (int i = 0; i < n; ++i) {
        if (!visited[i])
            return false;
    }
    fill(visited.begin(), visited.end(), false);
    dfs(0, radj, dfs);
    for (int i = 0; i < n; ++i) {
        if (!visited[i])
            return false;
    }
    return true;
}
int main() {
    cin >> n;
    w.assign(n, vector<int>(n));
    int maxWeight = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            cin >> w[i][j];
            maxWeight = max(maxWeight, w[i][j]);
        }
    }
    int left = 0, right = maxWeight;
    while (left < right) {
        int mid = (left + right) / 2;
        if (stronglyConnected(mid)) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    cout << left << endl;
    return 0;
}
