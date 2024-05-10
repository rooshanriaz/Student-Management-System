// Simulated data
let users = [];

// Admin Page logic
document.getElementById("manageUsersForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;
    
    // Simulate creating a new user
    users.push({ username, password, role });
    console.log("User created:", { username, password, role });
});

document.getElementById("allotHostelForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const studentName = document.getElementById("studentName").value;
    const hostel = document.getElementById("hostel").value;
    const roomNumber = document.getElementById("roomNumber").value;
    
    // Simulate allotting hostel to student
    console.log(`${studentName} allotted Room ${roomNumber} in Hostel ${hostel}`);
});

document.getElementById("allotMessHallForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const studentName = document.getElementById("studentNameMess").value;
    const messHall = document.getElementById("messHall").value;
    
    // Simulate allotting mess hall to student
    console.log(`${studentName} allotted Mess Hall ${messHall}`);
});
