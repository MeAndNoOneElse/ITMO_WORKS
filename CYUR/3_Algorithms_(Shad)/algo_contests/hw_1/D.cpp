#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

static bool CanCoverAtLeast(
    const std::vector<std::pair<double, double>>& intervals, int required_k) {
    std::vector<double> starts;
    std::vector<double> ends;
    starts.reserve(intervals.size());
    ends.reserve(intervals.size());
    for (const auto& interval_pair : intervals) {
        starts.push_back(interval_pair.first);
        ends.push_back(interval_pair.second);
    }
    std::sort(starts.begin(), starts.end());
    std::sort(ends.begin(), ends.end());

    size_t start_index = 0;
    int current_count = 0;
    for (size_t end_index = 0; end_index < ends.size(); ++end_index) {
        while (start_index < starts.size() &&
               starts[start_index] <= ends[end_index]) {
            ++current_count;
            ++start_index;
        }
        if (current_count >= required_k) {
            return true;
        }
        --current_count;
    }
    return false;
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int point_count_n = 0;
    int required_k = 0;
    std::cin >> point_count_n >> required_k;

    std::vector<int> x_coords(point_count_n);
    std::vector<int> y_coords(point_count_n);
    for (int index = 0; index < point_count_n; ++index) {
        std::cin >> x_coords[index] >> y_coords[index];
    }

    double left_radius = 0.0;
    const double kMaxInitialRadius = 3000.0;
    double right_radius = kMaxInitialRadius;
    const double kPrecision = 1e-4;

    while (right_radius - left_radius > kPrecision) {
        const double kHalfFactor = 2.0;
        double middle_radius = (left_radius + right_radius) / kHalfFactor;
        std::vector<std::pair<double, double>> intervals;
        intervals.reserve(point_count_n);

        for (int index = 0; index < point_count_n; ++index) {
            double x_val = static_cast<double>(x_coords[index]);
            double y_val = static_cast<double>(y_coords[index]);
            double y_sq = y_val * y_val;
            if (y_sq > middle_radius * middle_radius) {
                continue;
            }
            double delta = std::sqrt((middle_radius * middle_radius) - y_sq);
            intervals.push_back(std::make_pair(x_val - delta, x_val + delta));
        }

        if (CanCoverAtLeast(intervals, required_k)) {
            right_radius = middle_radius;
        } else {
            left_radius = middle_radius;
        }
    }

    std::cout.setf(std::ios::fixed);
    const int kOutputPrecision = 6;
    std::cout.precision(kOutputPrecision);
    std::cout << right_radius << '\n';

    return 0;
}
