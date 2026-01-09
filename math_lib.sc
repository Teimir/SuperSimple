// Mathematical library for sc language
// Uses fixed-point arithmetic with scale 10000 (1.0 = 10000)

// Constants in fixed-point format (multiplied by 10000)
// PI ≈ 3.141592653589793
// E ≈ 2.718281828459045
// LN_10 ≈ 2.302585092994046

// Helper function: factorial
function factorial(n) {
    if (n == 0 || n == 1) {
        return 1;
    }
    uint32 result = 1;
    uint32 i = 2;
    while (i <= n) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

// Helper function: normalize angle to [-PI, PI] range
function normalize_angle(x) {
    // PI in fixed-point: 31416
    uint32 pi = 31416;
    uint32 two_pi = 62832;
    
    // Handle negative angles by converting to positive equivalent
    // Since we're using uint32, we need to handle this carefully
    // For now, we'll work with positive angles and adjust at the end
    
    // Reduce to [0, 2*PI] range
    while (x > two_pi) {
        x = x - two_pi;
    }
    
    // Convert to [-PI, PI] range
    if (x > pi) {
        x = x - two_pi;
    }
    
    return x;
}

// Power function: base^exponent (for positive integer exponents)
// For fixed-point base, result is also in fixed-point
function power(base, exponent) {
    if (exponent == 0) {
        return 10000;  // 1 in fixed-point
    }
    if (exponent == 1) {
        return base;
    }
    
    uint32 result = 10000;  // Start with 1 in fixed-point
    uint32 exp = exponent;
    uint32 b = base;
    
    // Fast exponentiation using binary method
    // For fixed-point: if base is in fixed-point, we need to adjust
    // For simplicity, assume base is a regular integer (not fixed-point)
    // If base is in fixed-point, the result will be scaled accordingly
    
    while (exp > 0) {
        if (exp & 1) {
            // For fixed-point multiplication: (result * b) / 10000
            result = (result * b) / 10000;
        }
        b = (b * b) / 10000;  // Square in fixed-point
        exp = exp >> 1;
    }
    
    return result;
}

// Sine function using Taylor series
// sin(x) ≈ x - x³/3! + x⁵/5! - x⁷/7! + x⁹/9! - ...
// x is in fixed-point format (radians * 10000)
function sin(x) {
    // Normalize angle to [-PI, PI]
    x = normalize_angle(x);
    
    // First term: x (already in fixed-point)
    uint32 result = x;
    
    // Calculate x² once
    uint32 x_squared = (x * x) / 10000;
    
    // Build up x^n incrementally
    uint32 x_power = x_squared;  // Start with x²
    x_power = (x_power * x) / 10000;  // Now x³
    
    uint32 sign = 1;  // Start with negative (subtract x³/3!)
    uint32 n = 3;
    
    // Calculate terms up to x^9/9! for reasonable accuracy
    while (n <= 9) {
        // Calculate n!
        uint32 fact = factorial(n);
        
        // Calculate term: x^n / n!
        // x_power is already x^n in fixed-point
        // We need: (x_power * 10000) / fact to get the term value
        uint32 term_value = (x_power * 10000) / fact;
        
        // Apply sign and add/subtract term
        if (sign == 1) {
            result = result - term_value;
            sign = 0;
        } else {
            result = result + term_value;
            sign = 1;
        }
        
        // Prepare for next iteration: multiply by x² to get next odd power
        x_power = (x_power * x_squared) / 10000;
        n = n + 2;
    }
    
    return result;
}

// Cosine function using Taylor series
// cos(x) ≈ 1 - x²/2! + x⁴/4! - x⁶/6! + x⁸/8! - ...
// x is in fixed-point format (radians * 10000)
function cos(x) {
    // Normalize angle to [-PI, PI]
    x = normalize_angle(x);
    
    // First term: 1 (in fixed-point)
    uint32 result = 10000;
    
    // Calculate x² once
    uint32 x_squared = (x * x) / 10000;
    
    // Build up x^n incrementally (even powers)
    uint32 x_power = x_squared;  // Start with x²
    
    uint32 sign = 1;  // Start with negative (subtract x²/2!)
    uint32 n = 2;
    
    // Calculate terms up to x^8/8! for reasonable accuracy
    while (n <= 8) {
        // Calculate n!
        uint32 fact = factorial(n);
        
        // Calculate term: x^n / n!
        // x_power is already x^n in fixed-point
        uint32 term_value = (x_power * 10000) / fact;
        
        // Apply sign and add/subtract term
        if (sign == 1) {
            result = result - term_value;
            sign = 0;
        } else {
            result = result + term_value;
            sign = 1;
        }
        
        // Prepare for next iteration: multiply by x² to get next even power
        x_power = (x_power * x_squared) / 10000;
        n = n + 2;
    }
    
    return result;
}

// Tangent function: tan(x) = sin(x) / cos(x)
function tan(x) {
    uint32 s = sin(x);
    uint32 c = cos(x);
    
    // Avoid division by zero
    if (c == 0) {
        // Return a large value or error indicator
        // In fixed-point, we'll return a scaled large value
        return 100000000;  // Represents a very large number
    }
    
    // tan = sin / cos in fixed-point: (s * 10000) / c
    return (s * 10000) / c;
}

// Cotangent function: cot(x) = cos(x) / sin(x)
function cot(x) {
    uint32 s = sin(x);
    uint32 c = cos(x);
    
    // Avoid division by zero
    if (s == 0) {
        // Return a large value or error indicator
        return 100000000;  // Represents a very large number
    }
    
    // cot = cos / sin in fixed-point: (c * 10000) / s
    return (c * 10000) / s;
}

// Natural logarithm using series approximation
// For x close to 1: ln(x) ≈ (x-1) - (x-1)²/2 + (x-1)³/3 - (x-1)⁴/4 + ...
// x is in fixed-point format (x * 10000)
function ln(x) {
    // x must be positive and in fixed-point format
    if (x <= 0) {
        return 0;  // Error: logarithm of non-positive number
    }
    
    // If x equals 1 (10000 in fixed-point), ln(1) = 0
    if (x == 10000) {
        return 0;
    }
    
    // For better accuracy, we'll reduce x to range [0.5, 2] by using
    // ln(x) = ln(x * 2^k) - k * ln(2)
    // But for simplicity, we'll use direct series for x in reasonable range
    
    // Use series: ln(x) ≈ (x-1) - (x-1)²/2 + (x-1)³/3 - (x-1)⁴/4 + ...
    uint32 x_minus_one = x - 10000;  // (x - 1) in fixed-point
    
    // First term: (x - 1)
    uint32 result = x_minus_one;
    
    // Build up (x-1)^n incrementally
    uint32 x_minus_one_power = x_minus_one;
    uint32 sign = 1;  // Start with negative (subtract (x-1)²/2)
    uint32 n = 2;
    
    // Calculate terms up to (x-1)^6/6 for reasonable accuracy
    while (n <= 6) {
        // Calculate (x-1)^n
        x_minus_one_power = (x_minus_one_power * x_minus_one) / 10000;
        
        // Calculate term: (x-1)^n / n
        // In fixed-point: (x_minus_one_power * 10000) / n
        uint32 term_value = (x_minus_one_power * 10000) / n;
        
        // Apply sign and add/subtract term
        if (sign == 1) {
            result = result - term_value;
            sign = 0;
        } else {
            result = result + term_value;
            sign = 1;
        }
        
        n = n + 1;
    }
    
    return result;
}

// Base-10 logarithm: log10(x) = ln(x) / ln(10)
function log10(x) {
    // ln(10) in fixed-point ≈ 23026
    uint32 ln_10 = 23026;
    uint32 ln_x = ln(x);
    
    // log10(x) = ln(x) / ln(10) in fixed-point: (ln_x * 10000) / ln_10
    return (ln_x * 10000) / ln_10;
}

// Convert int32 to ASCII character array
// Fills the output array with ASCII codes of digits
// Returns the length of the string (number of characters)
// Note: Since arrays cannot be passed as parameters in sc, this function
// should be inlined or the array should be accessed directly in the caller
// This is a helper function that works with a local array
function int32_to_ascii_helper(value) {
    // Local array for output (caller should copy from this)
    uint32 output_array[12];
    // Handle zero case
    if (value == 0) {
        output_array[0] = 48;  // '0' in ASCII
        return 1;
    }
    
    // Temporary array to store digits in reverse order
    uint32 digits[12];  // Max 11 digits for int32 (including sign)
    uint32 count = 0;
    uint32 is_negative = 0;
    
    // Handle negative numbers
    // Check if value is negative (in two's complement, MSB indicates sign)
    // For int32, values >= 0x80000000 are negative
    uint32 sign_bit = value & 0x80000000;
    if (sign_bit != 0) {
        is_negative = 1;
        // Convert to positive: negate the value
        value = -value;
    }
    
    // Extract digits (right to left)
    uint32 abs_value = value;  // Now positive
    while (abs_value > 0) {
        uint32 digit = abs_value % 10;
        digits[count] = digit;
        count = count + 1;
        abs_value = abs_value / 10;
    }
    
    // Write to output array (left to right)
    uint32 output_index = 0;
    
    // Write minus sign if negative
    if (is_negative) {
        output_array[output_index] = 45;  // '-' in ASCII
        output_index = output_index + 1;
    }
    
    // Write digits in correct order (reverse of what we extracted)
    uint32 i = count;
    while (i > 0) {
        i = i - 1;
        uint32 digit = digits[i];
        output_array[output_index] = 48 + digit;  // Convert digit to ASCII ('0' + digit)
        output_index = output_index + 1;
    }
    
    return output_index;  // Return length of string
}
