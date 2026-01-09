// Division and modulo library for sc language
// Provides division and modulo operations for int32 and uint32 types

// Unsigned division: uint32 / uint32
function udiv(dividend, divisor) {
    if (divisor == 0) {
        return 0;  // Division by zero - return 0 as error indicator
    }
    
    if (dividend < divisor) {
        return 0;  // Dividend is smaller, result is 0
    }
    
    if (divisor == 1) {
        return dividend;  // Division by 1
    }
    
    // Optimized long division using bit shifts
    // Find the highest bit position where divisor can be shifted
    uint32 quotient = 0;
    uint32 remainder = dividend;
    
    // Find the highest power of 2 that divisor can be multiplied by
    uint32 temp_divisor = divisor;
    uint32 shift = 0;
    
    // Shift divisor left until it's larger than dividend
    while (temp_divisor <= remainder && shift < 32) {
        temp_divisor = temp_divisor << 1;
        shift = shift + 1;
    }
    
    // Now shift back one position
    if (shift > 0) {
        shift = shift - 1;
        temp_divisor = temp_divisor >> 1;
    }
    
    // Perform division using binary long division
    // Continue while shift is valid (not 0xFFFFFFFF) and remainder >= divisor
    uint32 shift_valid = 1;
    while (shift_valid != 0 && remainder >= divisor) {
        if (remainder >= temp_divisor) {
            remainder = remainder - temp_divisor;
            quotient = quotient + (1 << shift);
        }
        temp_divisor = temp_divisor >> 1;
        if (shift > 0) {
            shift = shift - 1;
        } else {
            shift_valid = 0;  // Exit loop when shift reaches 0
        }
    }
    
    return quotient;
}

// Unsigned modulo: uint32 % uint32
function umod(dividend, divisor) {
    if (divisor == 0) {
        return 0;  // Division by zero - return 0 as error indicator
    }
    
    if (dividend < divisor) {
        return dividend;  // Dividend is smaller, remainder is dividend
    }
    
    if (divisor == 1) {
        return 0;  // Division by 1, remainder is 0
    }
    
    // Optimized modulo using binary long division (same as udiv but return remainder)
    uint32 remainder = dividend;
    
    // Find the highest power of 2 that divisor can be multiplied by
    uint32 temp_divisor = divisor;
    uint32 shift = 0;
    
    // Shift divisor left until it's larger than dividend
    while (temp_divisor <= remainder && shift < 32) {
        temp_divisor = temp_divisor << 1;
        shift = shift + 1;
    }
    
    // Now shift back one position
    if (shift > 0) {
        shift = shift - 1;
        temp_divisor = temp_divisor >> 1;
    }
    
    // Perform modulo using binary long division
    // Continue while shift is valid (not 0xFFFFFFFF) and remainder >= divisor
    uint32 shift_valid = 1;
    while (shift_valid != 0 && remainder >= divisor) {
        if (remainder >= temp_divisor) {
            remainder = remainder - temp_divisor;
        }
        temp_divisor = temp_divisor >> 1;
        if (shift > 0) {
            shift = shift - 1;
        } else {
            shift_valid = 0;  // Exit loop when shift reaches 0
        }
    }
    
    return remainder;
}

// Signed division: int32 / int32
function sdiv(dividend, divisor) {
    if (divisor == 0) {
        return 0;  // Division by zero - return 0 as error indicator
    }
    
    // Handle sign
    uint32 is_dividend_negative = 0;
    uint32 is_divisor_negative = 0;
    uint32 abs_dividend = dividend;
    uint32 abs_divisor = divisor;
    
    // Check if dividend is negative
    uint32 sign_bit = dividend & 0x80000000;
    if (sign_bit != 0) {
        is_dividend_negative = 1;
        abs_dividend = -dividend;  // Make positive
    }
    
    // Check if divisor is negative
    sign_bit = divisor & 0x80000000;
    if (sign_bit != 0) {
        is_divisor_negative = 1;
        abs_divisor = -divisor;  // Make positive
    }
    
    // Perform unsigned division on absolute values
    uint32 quotient = udiv(abs_dividend, abs_divisor);
    
    // Apply sign: result is negative if signs differ
    if (is_dividend_negative != is_divisor_negative) {
        quotient = -quotient;  // Negate result
    }
    
    return quotient;
}

// Signed modulo: int32 % int32
function smod(dividend, divisor) {
    if (divisor == 0) {
        return 0;  // Division by zero - return 0 as error indicator
    }
    
    // Handle sign for dividend
    uint32 is_dividend_negative = 0;
    uint32 abs_dividend = dividend;
    uint32 abs_divisor = divisor;
    
    // Check if dividend is negative
    uint32 sign_bit = dividend & 0x80000000;
    if (sign_bit != 0) {
        is_dividend_negative = 1;
        abs_dividend = -dividend;  // Make positive
    }
    
    // Make divisor positive (modulo result sign follows dividend)
    sign_bit = divisor & 0x80000000;
    if (sign_bit != 0) {
        abs_divisor = -divisor;  // Make positive
    }
    
    // Perform unsigned modulo on absolute values
    uint32 remainder = umod(abs_dividend, abs_divisor);
    
    // Apply sign: result has same sign as dividend
    if (is_dividend_negative) {
        remainder = -remainder;  // Negate result
    }
    
    return remainder;
}

// Fast unsigned division using bit shifts (more efficient for powers of 2)
function udiv_fast(dividend, divisor) {
    if (divisor == 0) {
        return 0;
    }
    
    // Check if divisor is a power of 2
    // A number is a power of 2 if (n & (n-1)) == 0
    uint32 divisor_minus_one = divisor - 1;
    if ((divisor & divisor_minus_one) == 0) {
        // Divisor is power of 2, use bit shift
        // Find the shift amount
        uint32 shift = 0;
        uint32 temp = divisor;
        while (temp > 1) {
            temp = temp >> 1;
            shift = shift + 1;
        }
        return dividend >> shift;
    }
    
    // Not a power of 2, use regular division
    return udiv(dividend, divisor);
}

// Fast unsigned modulo using bit operations (more efficient for powers of 2)
function umod_fast(dividend, divisor) {
    if (divisor == 0) {
        return 0;
    }
    
    // Check if divisor is a power of 2
    uint32 divisor_minus_one = divisor - 1;
    if ((divisor & divisor_minus_one) == 0) {
        // Divisor is power of 2, use bit mask
        return dividend & divisor_minus_one;
    }
    
    // Not a power of 2, use regular modulo
    return umod(dividend, divisor);
}
