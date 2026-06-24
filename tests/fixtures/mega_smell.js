// A highly complex file designed to trigger all Clean Code rules

// 1. Dead Code (Function never called)
// 2. Too Many Parameters (> 3)
// 3. Data Clumps (Shares x, y, z with legacyProcessor)
function processBankTransaction(x, y, z, status, type) {
    // 4. Short Variable Names
    let a = x + y;
    let b = z * 2;

    // 5. Magic Numbers
    let max = 999.5;
    let tax = 15.0;

    // 6. Deep Nesting (> 3 levels)
    // 7. High Cyclomatic Complexity
    // 8. Multiple Responsibilities (calling db, api, email)
    // 9. Long Method (> 20 lines)
    if (a > 0) {
        if (b < max) {
            if (status === "ACTIVE") {
                if (type !== "TEST") {
                    console.log("Transaction starts with tax " + tax);

                    for (let i = 0; i < 10; i++) {
                        if (i % 2 === 0 && a !== b) {
                            console.log("Even processing: " + i);
                        } else if (i % 3 === 0) {
                            console.log("Odd processing: " + i);
                        }
                    }

                    // Triggering multiple responsibilities (Concerns)
                    saveToDatabase(x);
                    fetchFromApi(y);
                    sendEmailAlert(z);
                    generatePdfReport();

                    // Padding the method to easily exceed 20 lines
                    console.log("Logging step 1...");
                    console.log("Logging step 2...");
                    console.log("Logging step 3...");
                    console.log("Logging step 4...");
                    console.log("Logging step 5...");
                    console.log("Logging step 6...");
                    console.log("Logging step 7...");
                }
            }
        }
    }
    return a + b;
}

// Another function to trigger Data Clumps with processBankTransaction
function legacyProcessor(x, y, z) {
    let t = x * y * z; // Short variable
    return t;
}

// Dummy functions to satisfy the AST calls without crashing
function saveToDatabase(val) { }
function fetchFromApi(val) { }
function sendEmailAlert(val) { }
function generatePdfReport() { }
