#pragma once

#ifndef INTELLIGENT_ENGINEERING_VALIDATION_AGENT_VALIDATOR_HPP
#define INTELLIGENT_ENGINEERING_VALIDATION_AGENT_VALIDATOR_HPP

struct ValidationResult {
    double stress_pa;
    double allowable_stress_pa;
    bool constraint_pass;
};

ValidationResult validate_beam(
    double load_n,
    double length_m,
    double width_m,
    double height_m,
    double allowable_stress_pa
);

#endif // INTELLIGENT_ENGINEERING_VALIDATION_AGENT_VALIDATOR_HPP
