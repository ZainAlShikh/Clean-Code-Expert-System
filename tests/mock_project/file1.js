function calculateTotal(price, taxRate, discount, userType) {
    if (userType === 'admin') {
        if (price > 100) {
            if (discount > 0) {
                if (taxRate > 0) {
                    return price * (1 - discount) * (1 + taxRate) * 0.9;
                }
            }
        }
    }
    return price;
}

function dataClumpFuncA(a, b, c) {
    return a + b + c;
}

function dataClumpFuncB(a, b, c) {
    return a * b * c;
}

function processPayment(amount) {
    let fee = amount * 0.035;
    return amount + fee;
}

function usedFunction(x) {
    return x * 2;
}

function unusedFunction() {
    return "I am dead code";
}
