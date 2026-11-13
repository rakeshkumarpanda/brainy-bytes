# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "matrix_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

def mat_vec(M, v):
    result = []
    for row in M:                     # one dot product per row
        total = 0
        for a, b in zip(row, v):
            total = total + a * b
        result.append(total)
    return result

def mat_mul(A, B):
    rows = len(A)
    cols = len(B[0])
    inner = len(B)
    C = []
    for i in range(rows):
        new_row = []
        for j in range(cols):
            total = 0
            for k in range(inner):
                total = total + A[i][k] * B[k][j]
            new_row.append(total)
        C.append(new_row)
    return C

M = [[2, 1],
     [0, 1]]
print("M x (1, 2) =", mat_vec(M, [1, 2]))
print("M x M =", mat_mul(M, M))
I = [[1, 0], [0, 1]]
print("M x I =", mat_mul(M, I), "(the identity changes nothing)")
