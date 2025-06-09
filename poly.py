import gmpy2
from gmpy2 import mpz


def evaluate(poly, points, p):
    return fast_multi_point_evaluation(poly, points, p)

def normalize_element(x, p):
    """Normalize element to F_p"""
    if isinstance(x, (int, float)):
        return mpz(x) % p
    if hasattr(x, 'numerator') and hasattr(x, 'denominator'):
        num = mpz(x.numerator) % p
        den = mpz(x.denominator) % p
        den_inv = gmpy2.invert(den, p)
        return (num * den_inv) % p
    return mpz(x) % p

def poly_mult(A, B, p):
    """Multiply two polynomials in F_p[x]"""
    if not A or not B:
        return []
    
    A = [normalize_element(a, p) for a in A]
    B = [normalize_element(b, p) for b in B]
    
    result = [0] * (len(A) + len(B) - 1)
    for i in range(len(A)):
        for j in range(len(B)):
            result[i + j] = (result[i + j] + A[i] * B[j]) % p
    return result

def poly_add(A, B, p):
    """Add two polynomials in F_p[x]"""
    if not A and not B:
        return []
    if not A:
        return [normalize_element(b, p) for b in B]
    if not B:
        return [normalize_element(a, p) for a in A]
    
    max_len = max(len(A), len(B))
    result = [0] * max_len
    
    for i in range(len(A)):
        result[i] = (result[i] + A[i]) % p
    for i in range(len(B)):
        result[i] = (result[i] + B[i]) % p
    
    return result

def poly_mod(A, B, p):
    """Compute A mod B in F_p[x]"""
    if not A:
        return []
    if not B:
        raise ValueError("Division by zero polynomial")
    
    A = [normalize_element(a, p) for a in A]
    B = [normalize_element(b, p) for b in B]
    
    # Remove leading zeros from B
    while B and B[-1] == 0:
        B.pop()
    if not B:
        raise ValueError("Division by zero polynomial")
    
    A = A[:]
    while len(A) >= len(B):
        # Remove leading zeros from A
        while A and A[-1] == 0:
            A.pop()
        if len(A) < len(B):
            break
        
        # Get leading coefficient and its inverse
        lead_coeff = A[-1]
        b_lead_inv = gmpy2.invert(mpz(B[-1]), p)
        factor = (lead_coeff * b_lead_inv) % p
        
        # Subtract factor * B * x^(deg(A) - deg(B))
        offset = len(A) - len(B)
        for i in range(len(B)):
            A[offset + i] = (A[offset + i] - factor * B[i]) % p
        
        # Remove leading zeros
        while A and A[-1] == 0:
            A.pop()
    
    return A

def poly_derivative(A, p):
    """Compute derivative of polynomial A"""
    if len(A) <= 1:
        return []
    return [(i * A[i]) % p for i in range(1, len(A))]

def evaluate_poly(poly, x, p):
    """Evaluate polynomial at point x using Horner's method"""
    if not poly:
        return 0
    result = 0
    for coeff in reversed(poly):
        result = (result * x + coeff) % p
    return result

def build_subproduct_tree(points, p):
    """Build subproduct tree for points"""
    if not points:
        return []
    
    tree = []
    # Base level: (x - point) polynomials
    level = [[-normalize_element(point, p), 1] for point in points]
    tree.append(level)
    
    while len(level) > 1:
        new_level = []
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                prod = poly_mult(level[i], level[i + 1], p)
            else:
                prod = level[i]
            new_level.append(prod)
        level = new_level
        tree.append(level)
    
    return tree

def fast_multi_point_evaluation(poly, points, p):
    """Evaluate polynomial at multiple points using subproduct tree"""
    if not points:
        return []
    if not poly:
        return [0] * len(points)
    
    # For small cases, use direct evaluation
    if len(points) <= 4:
        return [evaluate_poly(poly, x, p) for x in points]
    
    # Build subproduct tree
    tree = build_subproduct_tree(points, p)
    if not tree:
        return [evaluate_poly(poly, x, p) for x in points]
    
    # Start with the polynomial at the root
    remainders = [poly]
    
    # Traverse tree from top to bottom, computing remainders
    for level_idx in range(len(tree) - 1, 0, -1):
        new_remainders = []
        remainder_idx = 0
        
        for i in range(0, len(tree[level_idx - 1]), 2):
            if remainder_idx >= len(remainders):
                break
            
            current_remainder = remainders[remainder_idx]
            remainder_idx += 1
            
            # Left child remainder
            left_remainder = poly_mod(current_remainder, tree[level_idx - 1][i], p)
            new_remainders.append(left_remainder)
            
            # Right child remainder (if exists)
            if i + 1 < len(tree[level_idx - 1]):
                right_remainder = poly_mod(current_remainder, tree[level_idx - 1][i + 1], p)
                new_remainders.append(right_remainder)
        
        remainders = new_remainders
    
    # Evaluate final remainders at corresponding points
    results = []
    for i, point in enumerate(points):
        if i < len(remainders):
            val = evaluate_poly(remainders[i], point, p)
        else:
            val = evaluate_poly(poly, point, p)
        results.append(val)
    
    return results

def interpolate_recursive(tree, values, level, index, p):
    """
    Recursively construct interpolation polynomial using subproduct tree
    
    Args:
        tree: subproduct tree
        values: y-values scaled by derivative values (c_i = y_i / M'(x_i))
        level: current level in tree (0 = leaves, max = root)
        index: index at current level
        p: prime modulus
    
    Returns:
        Polynomial coefficients
    """
    # Base case: at leaf level
    if level == 0:
        if index < len(values):
            return [values[index] % p]
        else:
            return [0]
    
    # Recursive case: combine left and right subtrees
    left_idx = index * 2
    right_idx = index * 2 + 1
    
    # Get polynomials from children
    left_poly = interpolate_recursive(tree, values, level - 1, left_idx, p)
    right_poly = interpolate_recursive(tree, values, level - 1, right_idx, p) if right_idx < len(tree[level - 1]) else []
    
    # Get the polynomials to multiply with
    # For left subtree: multiply by right subproduct
    # For right subtree: multiply by left subproduct
    right_subproduct = tree[level - 1][right_idx] if right_idx < len(tree[level - 1]) else [1]
    left_subproduct = tree[level - 1][left_idx] if left_idx < len(tree[level - 1]) else [1]
    
    # Compute contributions
    left_contribution = poly_mult(left_poly, right_subproduct, p)
    right_contribution = poly_mult(right_poly, left_subproduct, p) if right_poly else []
    
    # Add contributions
    result = poly_add(left_contribution, right_contribution, p)
    
    return result

def fast_modular_interpolation(x, y, p):
    """
    Fast polynomial interpolation using subproduct tree approach
    Complexity: O(n log² n) operations in the field
    
    Args:
        x: list of x coordinates (must be distinct)
        y: list of y coordinates  
        p: prime modulus for finite field operations
    
    Returns:
        Polynomial coefficients [a0, a1, ..., an] representing interpolating polynomial
    """
    n = len(x)
    if n == 0:
        return []
    if n == 1:
        return [y[0] % p]
    
    # Check for duplicate points
    if len(set(x)) != len(x):
        raise ValueError("Points must be distinct for interpolation")
    
    # Step 1: Build subproduct tree
    tree = build_subproduct_tree(x, p)
    if not tree:
        return [y[0] % p]
    
    # Step 2: Get master polynomial M(x) = product of (x - x_i)
    master_poly = tree[-1][0]
    
    # Step 3: Compute derivative M'(x)
    master_deriv = poly_derivative(master_poly, p)
    
    # Step 4: Evaluate M'(x_i) for all points using fast multipoint evaluation
    deriv_values = fast_multi_point_evaluation(master_deriv, x, p)
    
    # Step 5: Compute c_i = y_i / M'(x_i) mod p
    scaled_values = []
    for i in range(n):
        if deriv_values[i] == 0:
            raise ValueError(f"Derivative is zero at point {x[i]}, points might not be distinct")
        
        inv_deriv = gmpy2.invert(mpz(deriv_values[i]), p)
        c_i = (y[i] * inv_deriv) % p
        scaled_values.append(c_i)
    
    # Step 6: Reconstruct interpolation polynomial using recursive approach
    result = interpolate_recursive(tree, scaled_values, len(tree) - 1, 0, p)
    
    # Remove trailing zeros
    while result and result[-1] == 0:
        result.pop()
    
    return result
