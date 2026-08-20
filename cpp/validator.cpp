#include "validator.hpp"
#include <cstdlib>
#include <iomanip>
#include <iostream>

ValidationResult validate_beam(
    double load_n,
    double length_m,
    double width_m,
    double height_m,
    double allowable_stress_pa
) {
    const double moment_nm = load_n * length_m / 4.0;
    const double stress_pa =
        6.0 * moment_nm / (width_m * height_m * height_m);

    return {
        stress_pa,
        allowable_stress_pa,
        stress_pa <= allowable_stress_pa
    };
}

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr
            << "Usage: validator load length width height allowable_stress\n";
        return 2;
    }

    const double load = std::atof(argv[1]);
    const double length = std::atof(argv[2]);
    const double width = std::atof(argv[3]);
    const double height = std::atof(argv[4]);
    const double allowable = std::atof(argv[5]);

    if (
        load <= 0 ||
        length <= 0 ||
        width <= 0 ||
        height <= 0 ||
        allowable <= 0
    ) {
        return 3;
    }

    ValidationResult result = validate_beam(
        load,
        length,
        width,
        height,
        allowable
    );

    std::cout << std::setprecision(17)
              << result.stress_pa << " "
              << result.allowable_stress_pa << " "
              << (result.constraint_pass ? "PASS" : "FAIL")
              << "\n";

    return 0;
}