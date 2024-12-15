function myFunction() {
    const correctPassword = "yourPassword";  // Replace with your desired password

    swal({
        title: "Enter password:",
        content: {
            element: "input",
            attributes: {
                placeholder: "Type your password",
                type: "password",
            },
        },
        buttons: ["Cancel", "Submit"],
    }).then((value) => {
        if (value) {
            if (value === correctPassword) {
                swal("You have entered!", "", "success");
            } else {
                swal("Incorrect password!", "Please try again.", "error").then(() => {
                    // Reprompt the user
                    myFunction();
                });
            }
        } else {
            // If user canceled the prompt, redirect them to home page
            window.location.href = '/';
        }
    });
}
