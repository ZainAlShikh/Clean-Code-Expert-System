function unusedFunction() {
    console.log("Nobody calls me");
}
function createUser(firstName, lastName, email, phoneNumber) {
    let status = 404; 
    if (firstName && lastName) {
        validateData(firstName);      
        db.save(firstName, lastName); 
        sendEmail(email);             
        logger.log("Created user");   
    }
}
function updateUser(firstName, lastName, email, phoneNumber) {
    db.save(firstName, lastName);
}
function complexAndLongTask(param1, param2, param3, param4, param5) {
    let x = 10; 
    let y = 20;
    if (param1) {
        if (param2) {
            if (param3) {
                if (param4) {
                    console.log("I am too deep!");
                }
            }
        }
    }
    if (param1 || param2 || param3 || param4 || param5) {
        console.log("Condition 1");
    }
    if (x == 10 && y == 20) {
        console.log("Condition 2");
    }
    for (let i = 0; i < 5; i++) {
        if (i === 1) { console.log("A"); }
        else if (i === 2) { console.log("B"); }
        else if (i === 3) { console.log("C"); }
    }
    console.log("Padding line 1");
    console.log("Padding line 2");
    console.log("Padding line 3");
    console.log("Padding line 4");
    console.log("Padding line 5");
    console.log("Padding line 6");
    console.log("Padding line 7");
    console.log("Padding line 8");
    console.log("Padding line 9");
    console.log("Padding line 10");
}
function validateData() { }
const db = { save: function () { } };
function sendEmail() { }
const logger = { log: function () { } };
createUser("John", "Doe", "john@example.com", "123456");
updateUser("John", "Doe", "john@example.com", "123456");
complexAndLongTask(1, 2, 3, 4, 5);
