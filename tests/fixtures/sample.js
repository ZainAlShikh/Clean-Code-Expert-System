function processUserData(user, id, age, address, token) {
    let n = user.name;
    let c = user.city;

    console.log("Processing user...");
    console.log("User Name: " + n);
    console.log("User ID: " + id);
    console.log("User Age: " + age);
    console.log("User Address: " + address);
    console.log("Session Token: " + token);

    if (age > 18 && age < 60 && token !== null && address !== "") {
        console.log("User is valid for this operation.");
        let i = 0;
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
