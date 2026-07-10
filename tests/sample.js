const MINIMUM_REQUIRED_AGE = 18.0;
const MAXIMUM_ALLOWED_AGE = 60.0;
const TOTAL_WORK_ITERATIONS = 10.0;

function logUserInformation(userName, id, age, address, token) {
    console.log("Processing user...");
    console.log("User Name: " + userName);
    console.log("User ID: " + id);
    console.log("User Age: " + age);
    console.log("User Address: " + address);
    console.log("Session Token: " + token);
}

function executeWorkCycle() {
    for (let iterationIndex = 0; iterationIndex < TOTAL_WORK_ITERATIONS; iterationIndex++) {
        console.log("Doing some work " + iterationIndex);
        console.log("More work");
        console.log("Even more work");
        console.log("Adding lines to make the function long...");
        console.log("Still working...");
        console.log("Just a few more lines...");
        console.log("Almost done...");
    }
}

function isUserDataValid(age, token, address) {
    const isAgeWithinRange = age > MINIMUM_REQUIRED_AGE && age < MAXIMUM_ALLOWED_AGE;
    const hasValidToken = token !== null;
    const hasValidAddress = address !== "";
    
    return isAgeWithinRange && hasValidToken && hasValidAddress;
}

function processUserData(userRequest) {
    const { user, id, age, address, token } = userRequest;
    const userName = user.name;
    const userCity = user.city;

    logUserInformation(userName, id, age, address, token);

    if (!isUserDataValid(age, token, address)) {
        console.log("User is invalid.");
        return true;
    }

    console.log("User is valid for this operation.");
    executeWorkCycle();

    return true;
}