#include <iostream>
#include <vector>

static int FindBestPosition(const std::vector<int>& array_a,
                            const std::vector<int>& array_b) {
    int length_l = static_cast<int>(array_a.size());
    int left_k = 1;
    int right_k = length_l;

    while (left_k < right_k) {
        int middle_k = (left_k + right_k) / 2;
        if (array_a[middle_k - 1] >= array_b[middle_k - 1]) {
            right_k = middle_k;
        } else {
            left_k = middle_k + 1;
        }
    }

    int best_k = left_k;
    int best_max = std::max(array_a[left_k - 1], array_b[left_k - 1]);

    if (left_k > 1) {
        int prev_k = left_k - 1;
        int prev_max = std::max(array_a[prev_k - 1], array_b[prev_k - 1]);
        if (prev_max < best_max) {
            best_max = prev_max;
            best_k = prev_k;
        }
    }

    (void)best_max;

    return best_k;
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int array_count_n = 0;
    int array_count_m = 0;
    int length_l = 0;
    std::cin >> array_count_n >> array_count_m >> length_l;

    std::vector<std::vector<int>> arrays_a(array_count_n,
                                           std::vector<int>(length_l));
    for (int index_n = 0; index_n < array_count_n; ++index_n) {
        for (int index_l = 0; index_l < length_l; ++index_l) {
            std::cin >> arrays_a[index_n][index_l];
        }
    }

    std::vector<std::vector<int>> arrays_b(array_count_m,
                                           std::vector<int>(length_l));
    for (int index_m = 0; index_m < array_count_m; ++index_m) {
        for (int index_l = 0; index_l < length_l; ++index_l) {
            std::cin >> arrays_b[index_m][index_l];
        }
    }

    int query_count_q = 0;
    std::cin >> query_count_q;

    for (int query_index = 0; query_index < query_count_q; ++query_index) {
        int index_i = 0;
        int index_j = 0;
        std::cin >> index_i >> index_j;
        --index_i;
        --index_j;

        int result_k = FindBestPosition(arrays_a[index_i], arrays_b[index_j]);
        std::cout << result_k << '\n';
    }

    return 0;
}
