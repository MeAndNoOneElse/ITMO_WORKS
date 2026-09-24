#include <algorithm>
#include <iostream>
#include <vector>

static std::vector<int> ReadSequence(int& length) {
    std::cin >> length;
    std::vector<int> sequence(length);
    for (int index = 0; index < length; ++index) {
        std::cin >> sequence[index];
    }
    return sequence;
}

static bool IsBetterSequence(const std::vector<int>& candidate,
                             const std::vector<int>& best) {
    if (candidate.size() != best.size()) {
        return candidate.size() > best.size();
    }
    for (size_t index = 0; index < candidate.size(); ++index) {
        if (candidate[index] != best[index]) {
            return candidate[index] < best[index];
        }
    }
    return false;
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int length = 0;
    std::vector<int> sequence = ReadSequence(length);

    std::vector<std::vector<int>> up_seq(length);
    std::vector<std::vector<int>> down_seq(length);

    for (int i = 0; i < length; ++i) {
        up_seq[i] = {i};
        down_seq[i] = {i};

        for (int j = 0; j < i; ++j) {
            if (sequence[j] < sequence[i]) {
                std::vector<int> candidate = down_seq[j];
                candidate.push_back(i);
                if (IsBetterSequence(candidate, up_seq[i])) {
                    up_seq[i] = candidate;
                }
            } else if (sequence[j] > sequence[i]) {
                std::vector<int> candidate = up_seq[j];
                candidate.push_back(i);
                if (IsBetterSequence(candidate, down_seq[i])) {
                    down_seq[i] = candidate;
                }
            }
        }
    }

    std::vector<int> best_sequence = up_seq[0];
    for (int i = 1; i < length; ++i) {
        if (IsBetterSequence(up_seq[i], best_sequence)) {
            best_sequence = up_seq[i];
        }
        if (IsBetterSequence(down_seq[i], best_sequence)) {
            best_sequence = down_seq[i];
        }
    }

    std::vector<int> result;
    result.reserve(best_sequence.size());
    for (int idx : best_sequence) {
        result.push_back(sequence[idx]);
    }

    const int kResultSize = static_cast<int>(result.size());
    for (int i = 0; i < kResultSize; ++i) {
        std::cout << result[i];
        if (i + 1 < kResultSize) {
            std::cout << ' ';
        } else {
            std::cout << '\n';
        }
    }

    return 0;
}
