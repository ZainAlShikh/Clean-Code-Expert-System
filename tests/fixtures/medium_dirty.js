// A file with moderate issues

function processOrder(userId, productId, q, price, discount, tax, couponCode) {
    let a = price * q;
    let b = a - discount;
    let c = b + tax;

    if (couponCode === "SUMMER2026") {
        if (userId !== 0) {
            c = c - 15.0; // Magic Number
        }
    }

    if (c < 0) {
        c = 0;
    }

    // Call external service
    let res = null;
    if (userId > 0) {
        res = "Success: " + c;
    } else {
        res = "Error: Invalid user";
    }
    
    return res;
}

function unusedFunction() {
    return 42;
}
