// A sample JS file with bad code smells for testing the Expert System

// 1. Long method smell
// 2. Too many parameters
function processUserData(user, id, age, address, token) {
    let n = user.name; // Short variable name
    let c = user.city; // Short variable name
    
    console.log("Processing user...");
    console.log("User Name: " + n);
    console.log("User ID: " + id);
    console.log("User Age: " + age);
    console.log("User Address: " + address);
    console.log("Session Token: " + token);
    
    // 3. Complex condition smell
    if (age > 18 && age < 60 && token !== null && address !== "") {
        console.log("User is valid for this operation.");
        let i = 0; // 'i' is allowed as an exception in loops, but here it's let
        for (i = 0; i < 10; i++) {
            console.log("Doing some work " + i);
            console.log("More work");
            console.log("Even more work");
            console.log("Adding lines to make the function long...");
            console.log("Still working...");
            console.log("Just a few more lines...");
            console.log("Almost done...");
        }
    } else {
        console.log("User is invalid.");
    }
    
    return true;
}
