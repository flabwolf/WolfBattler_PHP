k = 1
h(1,1) = 0
h(1,2) = 0
DO i = 1, 6 * n ** 2
    flag = 1
    DO j = 1, k
        IF(h(j, 1) == hh(i, 1).and.h(j, 2) == hh(i, 2)) THEN
            flag = 2
            break的なやつ
    END DO
    IF(flag == 1) THEN
        h(k, 1) = hh(i, 1)
        h(k, 2) = hh(i, 2)
        k += 1
END DO
        
        